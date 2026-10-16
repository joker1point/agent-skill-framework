"""Skills Manager 卫生审计（只读，不改任何数)。

三块：
  A. 上游状态清单：source_missing / local_only / update_available
  B. 投放完整性：747 条 target 的存在性 / 指向正确性 / 实体副本（拷贝即漂移）
  C. 三方对账：各 agent 目录实际技能 vs 库投放清单 vs discovered_skills

junction 判别：Windows 目录 junction 的 os.path.islink 为 False，
用 os.path.realpath 是否解析到中央库来判"真链接 / 实体副本 / 指向错误"。
"""
from __future__ import annotations

import os
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

DB = "C:/Users/biren/.skills-manager/skills-manager.db"
OUT = Path(__file__).parent / "report-hygiene.md"
sys.stdout.reconfigure(encoding="utf-8")


def norm(p: str) -> str:
    return os.path.normcase(os.path.normpath(p))


conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
cur = conn.cursor()

# ---------- A. 上游状态 ----------
rows_skills = list(cur.execute(
    "select name, update_status, coalesce(source_ref,''), coalesce(central_path,''), "
    "coalesce(last_check_error,''), coalesce(updated_at,'') from skills order by update_status, name"))
by_status = defaultdict(list)
for name, st, ref, cp, err, upd in rows_skills:
    by_status[st].append((name, ref, cp, err, upd))

# ---------- B. 投放完整性 ----------
targets = list(cur.execute(
    "select t.tool, t.target_path, t.mode, t.status, coalesce(s.central_path,'') "
    "from skill_targets t join skills s on s.id = t.skill_id"))
check = defaultdict(int)
broken, wrong, copies = [], [], []
for tool, tp, mode, status, cp in targets:
    if not os.path.exists(tp):
        check["断链/缺失"] += 1
        broken.append((tool, tp))
        continue
    rp = os.path.realpath(tp)
    if norm(rp) == norm(cp):
        check["正常指向中央库"] += 1
    elif norm(rp) == norm(tp):
        check["实体副本(非链接)"] += 1
        copies.append((tool, tp))
    else:
        check["指向错误"] += 1
        wrong.append((tool, tp, rp, cp))

central_bad = []
for name, st, ref, cp, err, upd in rows_skills:
    if not cp or not Path(cp).exists():
        central_bad.append((name, cp or "(空)", "目录缺失"))
    elif not (Path(cp) / "SKILL.md").exists():
        central_bad.append((name, cp, "缺 SKILL.md"))

# ---------- C. 三方对账 ----------
roots = defaultdict(set)
db_names = defaultdict(set)
for tool, tp, mode, status, cp in targets:
    roots[tool].add(os.path.dirname(os.path.normpath(tp)))
    db_names[tool].add(os.path.basename(os.path.normpath(tp)).lower())

recon = {}
root_missing = []
for tool, rootset in sorted(roots.items()):
    scanned = set()
    for root in rootset:
        rp = Path(root)
        if not rp.exists():
            root_missing.append((tool, root))
            continue
        for d in rp.iterdir():
            try:
                if (d / "SKILL.md").exists():
                    scanned.add(d.name.lower())
            except OSError:
                continue
    recon[tool] = (len(scanned), sorted(scanned - db_names[tool]), sorted(db_names[tool] - scanned))

disc_by_tool = defaultdict(list)
for tool, nm, fp, imported in cur.execute(
        "select tool, name_guess, found_path, coalesce(imported_skill_id, 0) from discovered_skills "
        "order by tool, name_guess"):
    disc_by_tool[tool].append((nm, fp, imported))

# ---------- E. 部署覆盖与库外热点 ----------
undeployed = [r[0] for r in cur.execute(
    "select name from skills s where not exists "
    "(select 1 from skill_targets t where t.skill_id = s.id) order by name")]

extra_count = defaultdict(int)
for tool, (n, extra, missing) in recon.items():
    for nm in extra:
        extra_count[nm] += 1
hot_extra = [(nm, c) for nm, c in sorted(extra_count.items(), key=lambda x: -x[1]) if c >= 2]
hot_detail = []
for nm, c in hot_extra:
    in_lib = cur.execute("select count(*) from skills where name = ?", (nm,)).fetchone()[0]
    hot_detail.append((nm, c, in_lib))

# ---------- 输出 ----------
L = []
L += [
    "# 卫生审计报告 · Skills Manager",
    "",
    f"- 生成：{datetime.now().strftime('%Y-%m-%d %H:%M')}（脚本可重跑：`python hygiene_audit.py`）",
    f"- 审计范围：{len(rows_skills)} 条库技能 / {len(targets)} 条投放记录 / {sum(len(v) for v in disc_by_tool.values())} 条扫描发现",
    "",
    "## A. 上游状态清单",
    "",
]
for st in ("source_missing", "local_only", "update_available", "up_to_date"):
    items = by_status.get(st, [])
    L.append(f"### {st}（{len(items)}）")
    if st == "up_to_date":
        L.append("- 全部正常，从略")
    elif items:
        L.append("| 技能 | source_ref | 备注 |")
        L.append("|---|---|---|")
        for name, ref, cp, err, upd in items[:80]:
            note = err[:60] if err else (f"updated {str(upd)[:10]}" if upd else "")
            L.append(f"| {name} | {ref[:70] or '(空)'} | {note} |")
        if len(items) > 80:
            L.append(f"| … | 共 {len(items)} 条 | |")
    L.append("")

L += [
    "## B. 投放完整性（junction 实测）",
    "",
    "| 分类 | 数量 |",
    "|---|---:|",
]
for k, v in sorted(check.items(), key=lambda x: -x[1]):
    L.append(f"| {k} | {v} |")
L.append(f"| 合计 | {sum(check.values())} |")
L.append("")
if broken:
    L += ["**断链/缺失**（agent 目录里没有这条）：", ""]
    L += [f"- {tool}: {tp}" for tool, tp in broken[:40]]
    L.append("")
if copies:
    L += ["**实体副本**（非链接——拷贝即漂移的源头）：", ""]
    L += [f"- {tool}: {tp}" for tool, tp in copies[:40]]
    L.append("")
if wrong:
    L += ["**指向错误**：", ""]
    L += [f"- {tool}: {tp} → {rp}" for tool, tp, rp, cp in wrong[:40]]
    L.append("")
if central_bad:
    L += ["**中央库本体异常**：", ""]
    L += [f"- {name}: {cp}（{why}）" for name, cp, why in central_bad[:40]]
    L.append("")

L += ["## C. 三方对账（各 agent 目录 vs 库投放）", "", "| agent | 盘上技能数 | 库外（盘上有、库没投放） | 库有盘上无 |", "|---|---:|---:|---:|"]
for tool, (n, extra, missing) in sorted(recon.items(), key=lambda x: -x[1][0]):
    L.append(f"| {tool} | {n} | {len(extra)} | {len(missing)} |")
L.append("")
for tool, (n, extra, missing) in sorted(recon.items()):
    if extra or missing:
        L.append(f"### {tool}")
        if extra:
            L.append(f"- 库外（前 30，共 {len(extra)}）：" + "、".join(extra[:30]))
        if missing:
            L.append(f"- 库有盘上无（前 30，共 {len(missing)}）：" + "、".join(missing[:30]))
        L.append("")
if root_missing:
    L += ["**根目录缺失**：", ""] + [f"- {t}: {r}" for t, r in root_missing] + [""]

L += ["## D. 待导入（discovered_skills）", "", "| agent | 待导入 | 已导入 |", "|---|---:|---:|"]
for tool, items in sorted(disc_by_tool.items()):
    imported = sum(1 for _, _, imp in items if imp)
    L.append(f"| {tool} | {len(items)} | {imported} |")
L.append("")
for tool, items in sorted(disc_by_tool.items()):
    pending = [nm for nm, _, imp in items if not imp]
    if pending:
        L.append(f"- {tool}（{len(pending)}）：" + "、".join(sorted(pending)[:40]))
L.append("")

L += [
    "",
    "## E. 部署覆盖与库外热点",
    "",
    f"- 库 {len(rows_skills)} 条中，**从未投放到任何 agent**：{len(undeployed)} 条",
    f"  - 名单（前 40）：" + "、".join(undeployed[:40]) + ("…" if len(undeployed) > 40 else ""),
    "",
    "**库外热点（≥2 个 agent 目录里有、但库未向它投放）**：",
    "",
    "| 技能 | 出现在几个 agent | 是否在库中 |",
    "|---|---:|---|",
]
for nm, c, in_lib in hot_detail:
    L.append(f"| {nm} | {c} | {'在库（未投放）' if in_lib else '不在库'} |")
L.append("")

OUT.write_text("\n".join(L) + "\n", encoding="utf-8")

# 控制台摘要
print(f"上游状态: " + " | ".join(f"{k}={len(v)}" for k, v in sorted(by_status.items())))
print("投放完整性:", dict(check), "合计", sum(check.values()))
print("中央库本体异常:", len(central_bad))
print("三方对账（盘上/库外/库有盘无）:")
for tool, (n, extra, missing) in sorted(recon.items(), key=lambda x: -x[1][0]):
    print(f"  {tool:14s} 盘上 {n:3d}  库外 {len(extra):3d}  库有盘无 {len(missing):2d}")
print("待导入:", {k: len(v) for k, v in sorted(disc_by_tool.items())})
print(f"\n已写入 {OUT}")
