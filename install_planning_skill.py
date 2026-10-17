"""
重新安装 planning-with-files skill
"""
import os
import sys
import json
import uuid
import time
import hashlib
import shutil
import sqlite3
import subprocess
from pathlib import Path

DB_PATH = os.path.expandvars(r"%USERPROFILE%\.skills-manager\skills-manager.db")
CENTRAL_SKILLS_DIR = Path(os.path.expandvars(r"%USERPROFILE%\.skills-manager\skills"))
PROJECT_SKILLS_DIR = Path(os.path.expandvars(r"%USERPROFILE%\Documents\trae_projects\0-1agent\.agents\skills"))

SKILL = {
    "name": "planning-with-files",
    "repo": "https://github.com/OthmanAdi/planning-with-files",
    "description": "把规划写进文件，上下文压缩了也不丢状态",
    "source": "社区",
}

def run_cmd(cmd, cwd=None):
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

# 克隆仓库
temp_dir = Path(os.path.expandvars(r"%USERPROFILE%\.skills-manager\temp-clones")) / SKILL['name']
if temp_dir.exists():
    try:
        shutil.rmtree(temp_dir)
    except:
        pass

print(f"克隆: {SKILL['repo']}")
code, stdout, stderr = run_cmd(f"git clone {SKILL['repo']} {temp_dir}")
if code != 0:
    print(f"克隆失败: {stderr[:200]}")
    sys.exit(1)

# 查看仓库结构
print("\n仓库结构:")
for root, dirs, files in os.walk(temp_dir):
    level = root.replace(str(temp_dir), '').count(os.sep)
    indent = ' ' * 2 * level
    print(f"{indent}{os.path.basename(root)}/")
    subindent = ' ' * 2 * (level + 1)
    for f in files[:5]:
        print(f"{subindent}{f}")

# 复制到central目录
target_dir = CENTRAL_SKILLS_DIR / SKILL['name']
target_dir.mkdir(parents=True, exist_ok=True)

# 复制所有文件
for item in temp_dir.iterdir():
    if item.name == ".git":
        continue
    if item.is_file():
        shutil.copy2(item, target_dir / item.name)
    elif item.is_dir():
        shutil.copytree(item, target_dir / item.name, dirs_exist_ok=True)

print(f"\n复制到: {target_dir}")

# 检查是否有SKILL.md
skill_file = target_dir / "SKILL.md"
if not skill_file.exists():
    skill_file = target_dir / "skill.md"
if skill_file.exists():
    print(f"找到SKILL.md: {skill_file}")
else:
    print("未找到SKILL.md，创建基础版本")
    skill_file.write_text(f"""---
name: {SKILL['name']}
description: {SKILL['description']}
tags: community, top10
---

# Planning with Files

{SKILL['description']}

**GitHub**: {SKILL['repo']}
""", encoding="utf-8")

# 注册到数据库
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("SELECT id FROM skills WHERE name = ?", (SKILL['name'],))
existing = cur.fetchone()
if existing:
    print(f"已存在，跳过注册")
else:
    content_hash = hashlib.sha256(skill_file.read_bytes()).hexdigest()
    now_ms = int(time.time() * 1000)
    skill_id = str(uuid.uuid4())
    
    cur.execute("""
        INSERT INTO skills (
            id, name, description, source_type, source_ref,
            source_ref_resolved, source_subpath, source_branch, source_revision,
            remote_revision, central_path, content_hash,
            enabled, created_at, updated_at, status, update_status,
            last_checked_at, last_check_error
        ) VALUES (?, ?, ?, ?, ?, NULL, NULL, NULL, NULL, NULL, ?, ?, 1, ?, ?, 'ok', 'up_to_date', ?, NULL)
    """, (
        skill_id, SKILL['name'], SKILL['description'],
        "import", SKILL['name'],
        str(target_dir), content_hash,
        now_ms, now_ms, now_ms
    ))
    
    for tag in ["top10", "community"]:
        cur.execute(
            "INSERT OR IGNORE INTO skill_tags (skill_id, tag) VALUES (?, ?)",
            (skill_id, tag)
        )
    
    print("注册成功")

conn.commit()
conn.close()

# 链接到项目
target_link = PROJECT_SKILLS_DIR / SKILL['name']
if target_link.exists():
    if target_link.is_symlink():
        target_link.unlink()
    else:
        shutil.rmtree(target_link)

try:
    cmd = f'mklink /D "{target_link}" "{target_dir}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"软链接成功: {target_link}")
    else:
        shutil.copytree(target_dir, target_link)
        print(f"已复制代替")
except:
    shutil.copytree(target_dir, target_link)
    print(f"已复制代替")

# 清理临时目录
try:
    shutil.rmtree(temp_dir.parent, ignore_errors=True)
except:
    pass

print("\n安装完成！")
