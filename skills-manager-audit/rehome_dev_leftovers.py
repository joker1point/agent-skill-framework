"""开发辅助"杂物"成员 → 改挂建议（只读草稿，可能不准，供人工审核）。

在 apply_dev_scenario_cleanup.py 执行后运行：对 开发辅助 里已无其他归属的成员，
用词法重合度推荐最合适的其他场景（候选 top3），或建议移出场景。
产出：report-dev-leftovers.md
"""
from __future__ import annotations

import os
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import jieba

DB = "%USERPROFILE%/.skills-manager/skills-manager.db"
OUT = Path(__file__).parent / "report-dev-leftovers.md"
sys.stdout.reconfigure(encoding="utf-8")


def toks(text: str) -> set[str]:
    return {w.lower() for w in jieba.cut(text or "") if len(w.strip()) >= 2}


conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
cur = conn.cursor()

skills = {r[0]: (r[1], r[2] or "") for r in cur.execute("select id, name, description from skills")}
scen = list(cur.execute("select id, name from scenarios"))
name_of = {sid: nm for sid, nm in scen}
member_names = defaultdict(list)
for nm, sname in cur.execute(
        "select s.name, sc.name from scenario_skills ss "
        "join skills s on s.id = ss.skill_id join scenarios sc on sc.id = ss.scenario_id"):
    member_names[sname].append(nm)

sid_dev = next(s for s, n in scen if n == "开发辅助")
leftovers = [r[0] for r in cur.execute(
    "select skill_id from scenario_skills where scenario_id = ?", (sid_dev,))]

# 场景画像：名称 token（权重 3）+ 成员名 token（权重 1）
profiles = {}
for s, n in scen:
    if n == "开发辅助":
        continue
    name_t = toks(n)
    member_t = set()
    for mn in member_names.get(n, []):
        member_t |= toks(mn)
    profiles[n] = (name_t, member_t)

rows = []
for k in leftovers:
    nm, desc = skills[k]
    st = toks(nm) | toks(desc)
    scored = []
    for scen_name, (name_t, member_t) in profiles.items():
        score = 3 * len(st & name_t) + len(st & member_t)
        if score:
            scored.append((score, scen_name))
    scored.sort(key=lambda x: (-x[0], x[1]))
    rows.append((nm, scored[:3]))

rows.sort(key=lambda r: (-(r[1][0][0] if r[1] else 0), r[0]))

L = [
    "# 开发辅助「杂物」改挂建议（草稿）",
    "",
    f"- 生成：{datetime.now().strftime('%Y-%m-%d %H:%M')}（`python rehome_dev_leftovers.py` 可重跑；只读）",
    f"- 范围：开发辅助 当前成员 {len(leftovers)} 条（已无其他场景归属的）",
    "- 说明：词法重合度打分（场景名 ×3 + 成员名 ×1），**只是草稿**——建议逐条人工确认；无候选的考虑从场景移出（保留在库）",
    "",
    "| 技能 | 候选 1 | 候选 2 | 候选 3 | 倾向 |",
    "|---|---|---|---|---|",
]
for nm, cands in rows:
    c = [f"{s}（{sc}）" for sc, s in cands] + ["", "", ""]
    bias = "改挂" if cands and cands[0][0] >= 3 else ("待定" if cands else "移出场景")
    L.append(f"| {nm} | {c[0]} | {c[1]} | {c[2]} | {bias} |")

OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L[:12]))
print(f"...（共 {len(rows)} 条）\n已写入 {OUT}")
