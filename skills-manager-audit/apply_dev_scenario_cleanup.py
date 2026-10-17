"""执行：开发辅助场景移出重复编组（含对应 skill-tools 绑定）。

安全设计：
  1) 检查疑似 Skills Manager 进程未运行
  2) WAL checkpoint + 备份主库（.bak.时间戳）
  3) 单事务：同批 skill_id 从 scenario_skills / scenario_skill_tools 删除
  4) 复核并打印前后对比
可重跑：重复执行时待删集合为空。
"""
from __future__ import annotations

import os
import shutil
import sqlite3
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

DB = Path(os.path.expandvars(r"%USERPROFILE%\.skills-manager\skills-manager.db"))
SCENARIO = "开发辅助"
sys.stdout.reconfigure(encoding="utf-8")

# 1) 进程检查
tasks = subprocess.run(["tasklist"], capture_output=True, text=True).stdout
hits = [l.strip() for l in tasks.splitlines() if "skill" in l.lower()]
if hits:
    sys.exit("检测到疑似 Skills Manager 进程，先退出再执行：\n" + "\n".join(hits))
print("进程检查通过 ✓")

# 2) checkpoint + 备份
conn = sqlite3.connect(str(DB))
conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
conn.commit()
conn.close()

bak = DB.with_name(f"skills-manager.db.bak.{time.strftime('%Y%m%d_%H%M%S')}")
shutil.copy2(DB, bak)
print(f"已备份：{bak}（{bak.stat().st_size:,} bytes）")

# 3) 计算待删集合并执行
conn = sqlite3.connect(str(DB))
cur = conn.cursor()
sid = cur.execute("select id from scenarios where name = ?", (SCENARIO,)).fetchone()[0]

members = [r[0] for r in cur.execute(
    "select skill_id from scenario_skills where scenario_id = ?", (sid,))]
other = defaultdict(set)
for s2, k2 in cur.execute(
        "select scenario_id, skill_id from scenario_skills where scenario_id != ?", (sid,)):
    other[k2].add(s2)
targets = [k for k in members if other[k]]

before_ss = cur.execute("select count(*) from scenario_skills where scenario_id = ?", (sid,)).fetchone()[0]
before_tools = cur.execute("select count(*) from scenario_skill_tools where scenario_id = ?", (sid,)).fetchone()[0]
total_ss = cur.execute("select count(*) from scenario_skills").fetchone()[0]
total_tools = cur.execute("select count(*) from scenario_skill_tools").fetchone()[0]
print(f"开发辅助成员 {before_ss}，其中重复编组（待移出）{len(targets)}")

if not targets:
    print("无待移出项（可能已执行过）")
else:
    ph = ",".join("?" * len(targets))
    cur.execute(f"delete from scenario_skills where scenario_id = ? and skill_id in ({ph})",
                [sid, *targets])
    n1 = cur.rowcount
    cur.execute(f"delete from scenario_skill_tools where scenario_id = ? and skill_id in ({ph})",
                [sid, *targets])
    n2 = cur.rowcount
    conn.commit()
    print(f"已删除：scenario_skills {n1} 行；scenario_skill_tools {n2} 行")

# 4) 复核
after_ss = cur.execute("select count(*) from scenario_skills where scenario_id = ?", (sid,)).fetchone()[0]
after_tools = cur.execute("select count(*) from scenario_skill_tools where scenario_id = ?", (sid,)).fetchone()[0]
print(f"开发辅助：成员 {before_ss} → {after_ss}；绑定 {before_tools} → {after_tools}")
print(f"全库：成员 {total_ss} → {cur.execute('select count(*) from scenario_skills').fetchone()[0]}；"
      f"绑定 {total_tools} → {cur.execute('select count(*) from scenario_skill_tools').fetchone()[0]}")
conn.close()
print("完成。")
