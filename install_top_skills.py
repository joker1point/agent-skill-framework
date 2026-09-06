"""
安装十大必装skill并做好分类
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

DB_PATH = r"C:\Users\biren\.skills-manager\skills-manager.db"
CENTRAL_SKILLS_DIR = Path(r"C:\Users\biren\.skills-manager\skills")
PROJECT_SKILLS_DIR = Path(r"C:\Users\biren\Documents\trae_projects\0-1agent\.agents\skills")
TEMP_CLONE_DIR = Path(r"C:\Users\biren\.skills-manager\temp-clones")

TOP_SKILLS = [
    {
        "name": "planning-with-files",
        "repo": "https://github.com/OthmanAdi/planning-with-files",
        "description": "把规划写进文件，上下文压缩了也不丢状态",
        "source": "社区",
        "category": "dev-productivity",
    },
    {
        "name": "superpowers",
        "repo": "https://github.com/obra/superpowers",
        "description": "20多个可组合Skill，覆盖开发全流程",
        "source": "社区",
        "category": "dev-tools",
    },
    {
        "name": "code-review",
        "repo": "https://github.com/anthropics/claude-plugins-official",
        "description": "多Agent并行审查，降低假阳性",
        "source": "官方",
        "category": "dev-tools",
        "subpath": "plugins/code-review",
    },
    {
        "name": "webapp-testing",
        "repo": "https://github.com/anthropics/skills",
        "description": "Playwright自动化，跑测试和截图",
        "source": "官方",
        "category": "dev-testing",
    },
    {
        "name": "code-simplifier",
        "repo": "https://github.com/anthropics/claude-plugins-official",
        "description": "写完再看一遍，重复逻辑合并成函数",
        "source": "官方",
        "category": "dev-tools",
        "subpath": "plugins/code-simplifier",
    },
    {
        "name": "ui-ux-pro-max",
        "repo": "https://github.com/nextlevelbuilder/ui-ux-pro-max-skill",
        "description": "67种风格+161套配色，告别AI审美",
        "source": "社区",
        "category": "design-creative",
    },
    {
        "name": "ralph-loop",
        "repo": "https://github.com/anthropics/claude-plugins-official",
        "description": "Hook拦截塞回去，直到做完",
        "source": "官方",
        "category": "dev-productivity",
        "subpath": "plugins/ralph-loop",
    },
]


def run_cmd(cmd, cwd=None):
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def clone_repo(repo_url, dest_dir):
    if dest_dir.exists():
        shutil.rmtree(dest_dir, ignore_errors=True)
    print(f"  克隆: {repo_url}")
    code, stdout, stderr = run_cmd(f"git clone {repo_url} {dest_dir}")
    if code != 0:
        print(f"    ✗ 克隆失败: {stderr[:100]}")
        return False
    print(f"    ✓ 克隆成功")
    return True


def find_skill_files(repo_dir):
    skill_files = []
    for root, dirs, files in os.walk(repo_dir):
        for f in files:
            if f.lower() == "skill.md":
                skill_files.append(Path(root) / f)
    return skill_files


def copy_skill(repo_dir, skill_name, subpath=None):
    source_dir = repo_dir
    if subpath:
        source_dir = repo_dir / subpath

    target_dir = CENTRAL_SKILLS_DIR / skill_name
    target_dir.mkdir(parents=True, exist_ok=True)

    skill_file = source_dir / "SKILL.md"
    if skill_file.exists():
        shutil.copy2(skill_file, target_dir / "SKILL.md")
        print(f"    ✓ 复制 SKILL.md")
    else:
        skill_file = source_dir / "skill.md"
        if skill_file.exists():
            shutil.copy2(skill_file, target_dir / "SKILL.md")
            print(f"    ✓ 复制 skill.md")
        else:
            print(f"    ⚠ 未找到SKILL.md，创建基础版本")
            (target_dir / "SKILL.md").write_text(f"""---
name: {skill_name}
description: 十大必装skill之一
tags: official, top10
---
""", encoding="utf-8")

    for item in source_dir.iterdir():
        if item.is_file() and item.name not in ["SKILL.md", "skill.md"]:
            shutil.copy2(item, target_dir / item.name)
        elif item.is_dir() and item.name != "__pycache__":
            shutil.copytree(item, target_dir / item.name, dirs_exist_ok=True)

    return target_dir


def register_to_db(conn, skill_name, description, skill_dir):
    cur = conn.cursor()
    cur.execute("SELECT id FROM skills WHERE name = ?", (skill_name,))
    existing = cur.fetchone()
    if existing:
        return f"  = 已存在"

    skill_file = skill_dir / "SKILL.md"
    content_hash = ""
    if skill_file.exists():
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
        skill_id, skill_name, description,
        "import", skill_name,
        str(skill_dir), content_hash,
        now_ms, now_ms, now_ms
    ))

    for tag in ["top10", "official" if "官方" in description else "community"]:
        cur.execute(
            "INSERT OR IGNORE INTO skill_tags (skill_id, tag) VALUES (?, ?)",
            (skill_id, tag)
        )

    return f"  + 已注册"


def link_to_project(skill_name):
    source = CENTRAL_SKILLS_DIR / skill_name
    target = PROJECT_SKILLS_DIR / skill_name

    if not source.exists():
        return f"    ✗ 源目录不存在"

    if target.exists():
        if target.is_symlink():
            target.unlink()
        else:
            shutil.rmtree(target)

    try:
        cmd = f'mklink /D "{target}" "{source}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return f"    ✓ 软链接成功"
        else:
            shutil.copytree(source, target)
            return f"    ⚠ 已复制"
    except:
        shutil.copytree(source, target)
        return f"    ⚠ 已复制"


def main():
    print("=" * 70)
    print("安装十大必装Skill")
    print("=" * 70)

    TEMP_CLONE_DIR.mkdir(parents=True, exist_ok=True)
    CENTRAL_SKILLS_DIR.mkdir(parents=True, exist_ok=True)
    PROJECT_SKILLS_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)

    for skill in TOP_SKILLS:
        print(f"\n{'-'*70}")
        print(f"安装: {skill['name']}")
        print(f"来源: {skill['source']}")
        print(f"描述: {skill['description']}")

        repo_dir = TEMP_CLONE_DIR / skill['name']
        if not clone_repo(skill['repo'], repo_dir):
            continue

        target_dir = copy_skill(repo_dir, skill['name'], skill.get('subpath'))
        reg_result = register_to_db(conn, skill['name'], skill['description'], target_dir)
        print(f"  数据库: {reg_result}")

        link_result = link_to_project(skill['name'])
        print(link_result)

        shutil.rmtree(repo_dir, ignore_errors=True)

    conn.commit()
    conn.close()
    shutil.rmtree(TEMP_CLONE_DIR, ignore_errors=True)

    print("\n" + "=" * 70)
    print("更新分类...")
    print("=" * 70)

    import classify_skills_v2

    print("\n" + "=" * 70)
    print("十大必装Skill安装完成！")
    print("=" * 70)


if __name__ == "__main__":
    main()
