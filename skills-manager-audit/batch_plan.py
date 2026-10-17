"""批量清理方案（只读生成，不写库）。

回答三件事：
  1) 开发辅助（100 条）瘦身：哪些成员已在更具体场景里 → 建议从 开发辅助 移出
  2) 104 条"未投放"分类：盘上活跃 / 已属场景未投放 / 真孤儿
  3) 63 条 source_missing 分布与处置选项；error 2 条现状

产出：report-batch-plan.md（本目录）。"""
from __future__ import annotations

import os
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

DB = "%USERPROFILE%/.skills-manager/skills-manager.db"
OUT = Path(__file__).parent / "report-batch-plan.md"
sys.stdout.reconfigure(encoding="utf-8")


def est(text: str) -> int:
    cn = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
    return cn + max(1, round((len(text) - cn) / 4))


conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
cur = conn.cursor()

skills = {r[0]: (r[1], r[2] or "") for r in cur.execute("select id, name, description from skills")}
name_by_id = {k: v[0] for k, v in skills.items()}

scen = list(cur.execute("select id, name from scenarios order by name"))
name_of = {sid: nm for sid, nm in scen}
members = defaultdict(list)
for sid, kid in cur.execute("select scenario_id, skill_id from scenario_skills"):
    members[sid].append(kid)
sizes = {sid: len(v) for sid, v in members.items()}

member_scen = defaultdict(set)
for sid, kids in members.items():
    for k in kids:
        member_scen[k].add(sid)

tgt = defaultdict(int)
for kid, c in cur.execute("select skill_id, count(*) from skill_targets group by 1"):
    tgt[kid] = c

# 盘上技能名（15 个 agent 目录）
disk_names = set()
for (tp,) in cur.execute("select distinct target_path from skill_targets"):
    root = os.path.dirname(os.path.normpath(tp))
    if os.path.isdir(root):
        for d in os.listdir(root):
            disk_names.add(d.lower())

# ---- 1) 开发辅助瘦身 ----
sid_dev = next(s for s, n in scen if n == "开发辅助")
dev_ids = members[sid_dev]
move_out, keep_ids = [], []
for k in dev_ids:
    others = sorted((s for s in member_scen[k] if s != sid_dev), key=lambda s: sizes[s])
    if others:
        move_out.append((name_by_id[k], name_of[others[0]], sizes[others[0]]))
    else:
        keep_ids.append(k)
move_out.sort()
before_tok = sum(est(name_by_id[k] + ": " + skills[k][1]) for k in dev_ids)
after_tok = sum(est(name_by_id[k] + ": " + skills[k][1]) for k in keep_ids)

# ---- 2) 未投放分类 ----
und = [k for k in skills if tgt[k] == 0]
und_active = sorted(name_by_id[k] for k in und if name_by_id[k].lower() in disk_names)
und_in_scen = sorted(name_by_id[k] for k in und if member_scen[k] and name_by_id[k].lower() not in disk_names)
und_orphan = sorted(name_by_id[k] for k in und if not member_scen[k] and name_by_id[k].lower() not in disk_names)

# ---- 3) source_missing 分布 ----
sm = list(cur.execute("select name, coalesce(source_ref,'') from skills where update_status = ?", ("source_missing",)))
src_kind = defaultdict(int)
for _, ref in sm:
    low = ref.lower()
    if "workbuddy" in low:
        src_kind["workbuddy 市场目录"] += 1
    elif "qclaw" in low:
        src_kind["qclaw"] += 1
    elif not ref:
        src_kind["(空)"] += 1
    else:
        src_kind["其他"] += 1

errs = list(cur.execute("select name, substr(coalesce(last_check_error,''), 1, 60) from skills where update_status = ?", ("error",)))

# ---- 输出 ----
L = [
    "# 批量清理计划 · Skills Manager",
    "",
    f"- 生成：{datetime.now().strftime('%Y-%m-%d %H:%M')}（`python batch_plan.py` 可重跑；只读，不改库）",
    "",
    "## 0. 机制结论（先说清楚能做到什么）",
    "",
    "- `update_status` 值域只有 up_to_date / source_missing / update_available / error——**app 没有\"冻结/忽略\"状态**，靠改库伪造会被下一轮检查覆盖。",
    "- `enabled` 是唯一启停开关（当前 341 条全为 1）；自动更新是全局的（最近一次 2026-10-07）。",
    "- 结论：本计划里的动作分两类——**场景成员调整**（可在 app 场景管理里做）与**按需投放/归档**（内容决策）；不建议用 DB 伪状态。",
    "",
    "## 1. 开发辅助瘦身（核心）",
    "",
    f"- 现状：**{len(dev_ids)} 条 / ≈ {before_tok:,} token**（占库 24%）",
    f"- 其中 **{len(move_out)} 条已在更具体的场景里**（重复编组）；只有 {len(keep_ids)} 条是\"纯开发辅助\"成员",
    f"- 建议：把重复成员从 开发辅助 移出 → 瘦身后 **{len(keep_ids)} 条 / ≈ {after_tok:,} token**",
    "",
    f"### 建议移出（{len(move_out)} 条 → 只保留在其最具体场景）",
    "",
    "| 技能 | 保留在 | 该场景规模 |",
    "|---|---|---:|",
]
L += [f"| {n} | {s} | {c} |" for n, s, c in move_out]
L += ["", f"### 建议保留在 开发辅助（{len(keep_ids)} 条）", ""]
L.append("、".join(name_by_id[k] for k in sorted(keep_ids)))

L += [
    "",
    "## 2. 未投放清单（104 → 分三类）",
    "",
    f"- **盘上活跃但未纳入管理**：{len(und_active)} 条（这些在 agent 目录里存在，绕开 manager 分发，与\"第二事实源\"问题重叠）",
    "  - " + "、".join(und_active),
    f"- **已属场景但从未投放**：{len(und_in_scen)} 条（编了组、没投放——多半是有意保留在库里的仓库货）",
    "  - " + "、".join(und_in_scen[:60]) + ("…" if len(und_in_scen) > 60 else ""),
    f"- **真孤儿（不在任何场景）**：{len(und_orphan)} 条",
    "  - " + "、".join(und_orphan[:60]) + ("…" if len(und_orphan) > 60 else ""),
    "",
    "## 3. 上游异常（63 + 2）",
    "",
    f"- source_missing {len(sm)} 条，来源分布：" + "、".join(f"{k} {v}" for k, v in src_kind.items()),
    "  - 处置选项：① 保持现状（只是标记，无副作用）② 确认不用的直接归档删除 ③ 重新指定源（gh 等）。**不建议改 update_status 伪造状态。**",
]
if errs:
    L.append(f"- error {len(errs)} 条：" + "；".join(f"{n}（{e}）" for n, e in errs) + "——GitHub 连不上，等网络或删除源")

OUT.write_text("\n".join(L) + "\n", encoding="utf-8")

print(f"开发辅助：{len(dev_ids)} 条 / {before_tok:,} tok → 瘦身后 {len(keep_ids)} 条 / {after_tok:,} tok（移出 {len(move_out)} 条）")
print(f"未投放 104 → 盘上活跃 {len(und_active)} / 属场景未投放 {len(und_in_scen)} / 真孤儿 {len(und_orphan)}")
print(f"source_missing {len(sm)}：{dict(src_kind)}")
print(f"error {len(errs)}：{[n for n, _ in errs]}")
print(f"\n已写入 {OUT}")
