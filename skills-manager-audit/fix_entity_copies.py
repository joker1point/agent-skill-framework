"""把 qclaw 下的 4 条实体副本重链为 junction（指向中央库）。

背景（2026-10-09 审计）：
  .qclaw/skills/<name> 是实体目录（realpath 指向自身），而 DB target 记录声称 mode=symlink。
  内容与中央库 SKILL.md 逐字节一致，仅多 .DS_Store——修它零内容损失。

流程：qclaw 进程检查 → 备份 → mklink /J → 双验证（realpath + SKILL.md md5）。
可重复执行：已是正确 junction 的条目会跳过。
"""
from __future__ import annotations

import hashlib
import os
import pathlib
import shutil
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")

QCLAW = pathlib.Path(r"C:\Users\biren\.qclaw\skills")
CENTRAL = pathlib.Path(r"C:\Users\biren\.skills-manager\skills")
BACKUP = pathlib.Path(r"C:\Users\biren\.skills-manager\audit-backup-20261009")
NAMES = ["imap-smtp-email", "kdocs", "persona-switch", "tencent-meeting-mcp"]


def md5(p: pathlib.Path) -> str:
    f = p / "SKILL.md"
    return hashlib.md5(f.read_bytes()).hexdigest()[:8] if f.exists() else "MISSING"


def norm(p) -> str:
    return os.path.normcase(os.path.normpath(str(p)))


# 0. qclaw 进程检查
out = subprocess.run(["tasklist"], capture_output=True, text=True).stdout.lower()
if "qclaw" in out:
    sys.exit("检测到 qclaw 进程在运行——先退出 qclaw 再执行本脚本。")
print("qclaw 未在运行 ✓")

BACKUP.mkdir(parents=True, exist_ok=True)
done = 0

for n in NAMES:
    link = QCLAW / n
    target = CENTRAL / n
    print(f"\n== {n} ==")

    if not target.exists():
        print(f"  跳过：中央库目标不存在 {target}")
        continue

    if not link.exists():
        print("  链接不存在，直接创建")
    else:
        if norm(os.path.realpath(link)) == norm(target.resolve()):
            print("  已是正确 junction，跳过")
            done += 1
            continue
        dst = BACKUP / n
        i = 1
        while dst.exists():
            dst = BACKUP / f"{n}-{i}"
            i += 1
        shutil.move(str(link), str(dst))
        print(f"  已备份到 {dst}")

    r = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)],
                       capture_output=True, text=True)
    print("  mklink:", (r.stdout or r.stderr).strip()[:90])

    ok_link = norm(os.path.realpath(link)) == norm(target.resolve())
    same = md5(link) == md5(target)
    print(f"  验证：realpath→中央库 = {ok_link}；SKILL.md md5 一致 = {same}（{md5(link)} / {md5(target)}）")
    done += 1 if (ok_link and same) else 0

print(f"\n完成：{done}/{len(NAMES)} 条已确认为指向中央库的 junction。")
print(f"备份区：{BACKUP}（确认无误后可删）")
