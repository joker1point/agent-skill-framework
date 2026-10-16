"""场景装配预算报告（只读 Skills Manager 数据库）。

背景：库 341 条技能 → 30 个场景 → 15 个 agent。
回答：每个场景"装配"进上下文时有多重、哪些场景已经撑爆预算。

口径（粗估，只用于横向比较）：
  token ≈ 中文字符 ×1 + 其余字符 ÷4
预算阈值（可按需调整，改这里即可）：
  技能数：<=30 轻 / 31-60 中 / >60 重
  token ：<=6k 轻 / 6-12k 中 / >12k 重
"""
from __future__ import annotations

import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB = "C:/Users/biren/.skills-manager/skills-manager.db"
OUT = Path(__file__).parent / "report-assembly-budget.md"
sys.stdout.reconfigure(encoding="utf-8")


def est(text: str) -> int:
    cn = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
    return cn + max(1, round((len(text) - cn) / 4))


def grade(tok: int, n: int) -> str:
    if n > 60 or tok > 12000:
        return "重"
    if n > 30 or tok > 6000:
        return "中"
    return "轻"


conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
cur = conn.cursor()

skill_text = {
    r[0]: r[1]
    for r in cur.execute("select id, name || ': ' || coalesce(description, '') from skills")
}
lib_tokens = sum(est(v) for v in skill_text.values())
lib_rows = len(skill_text)

rows = []
# 注意：必须先 list() 物化——同一游标上再执行内层查询会冲掉外层结果集
for sid, sname in list(cur.execute("select id, name from scenarios order by name")):
    member_ids = [r[0] for r in cur.execute(
        "select skill_id from scenario_skills where scenario_id = ?", (sid,))]
    toks = sum(est(skill_text.get(i, "")) for i in member_ids)
    agents = cur.execute(
        "select count(distinct tool) from scenario_skill_tools where scenario_id = ?",
        (sid,)).fetchone()[0]
    rows.append((sname, len(member_ids), round(toks), agents))
rows.sort(key=lambda r: -r[2])

heavy = [r for r in rows if grade(r[2], r[1]) == "重"]
mid = [r for r in rows if grade(r[2], r[1]) == "中"]

lines = [
    "# 装配预算报告 · Skills Manager",
    "",
    f"- 生成：{datetime.now().strftime('%Y-%m-%d %H:%M')}（脚本可重跑：`python assemble_budget.py`）",
    f"- 库规模：**{lib_rows} 条技能**；全库摊开 ≈ **{lib_tokens:,} token**（= \"不装配、全量注入\" 的代价）",
    "- 口径：token ≈ 中文×1 + 其余字符÷4（粗估）；阈值：技能 ≤30 轻 / >60 重；token ≤6k 轻 / >12k 重",
    "",
    "| 场景 | 技能数 | token 估算 | 占库比 | agent 显式绑定 | 评级 |",
    "|---|---:|---:|---:|---:|---|",
]
for sname, n, toks, agents in rows:
    lines.append(f"| {sname} | {n} | {toks:,} | {toks / lib_tokens:.1%} | {agents}/15 | {grade(toks, n)} |")

lines += [
    "",
    "## 结论",
    f"- 重场景 {len(heavy)} 个、中场景 {len(mid)} 个；30 个场景装配合计 ≈ {sum(r[2] for r in rows):,} token（技能跨场景复用，未去重）",
]
if heavy:
    lines.append("- 最先该拆的：" + "、".join(f"{r[0]}（{r[1]} 条 / {r[2]:,} tok）" for r in heavy))
if mid:
    lines.append("- 观察名单：" + "、".join(f"{r[0]}（{r[1]} 条 / {r[2]:,} tok）" for r in mid))

lines += [
    "",
    "## 建议（阈值可调，改脚本顶部）",
    "- 单场景 >30 条 / >6k token：拆二级标签，或把低频技能改为\"按需检索\"而非常驻清单",
    "- agent 显式绑定 0/15 的场景：确认语义是\"默认全量投放\"还是\"漏配\"——两者体量可能差一个数量级",
    f"- 全库 {lib_tokens:,} token 是库层面全量注入的假想成本；agent 侧实际基线只有 36 条（另见投放报告），健康",
]

OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
print(f"\n已写入 {OUT}")
