"""
批量安装14个新skill到系统
流程：克隆GitHub仓库 → 提取SKILL.md → 注册到数据库 → 链接到项目
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

SKILLS_TO_INSTALL = [
    {
        "name": "avoid-ai-writing",
        "repo": "https://github.com/conorbronsdon/avoid-ai-writing",
        "description": "检测并避免AI生成的写作内容，保护原创性",
    },
    {
        "name": "design-doc-mermaid",
        "repo": "https://github.com/SpillwaveSolutions/design-doc-mermaid",
        "description": "使用Mermaid图表生成技术设计文档，可视化架构和流程图",
    },
    {
        "name": "csv-summarizer",
        "repo": "https://github.com/coffeefuelbump/csv-data-summarizer-claude-skill",
        "description": "CSV数据摘要生成器，自动分析和总结CSV文件内容",
    },
    {
        "name": "claude-task-master",
        "repo": "https://github.com/eyaltoledano/claude-task-master",
        "description": "任务管理大师，帮助规划、跟踪和完成复杂任务",
    },
    {
        "name": "ccpm",
        "repo": "https://github.com/automazeio/ccpm",
        "description": "Critical Chain Project Management，关键链项目管理技能",
    },
    {
        "name": "openai-skills",
        "repo": "https://github.com/openai/skills",
        "description": "OpenAI官方技能集，包含多个实用开发技能",
    },
    {
        "name": "expo-upgrade",
        "repo": "https://github.com/expo/skills",
        "description": "Expo项目升级技能，自动化升级Expo SDK和依赖",
    },
    {
        "name": "sentry-skills",
        "repo": "https://github.com/getsentry/skills",
        "description": "Sentry监控技能，帮助集成和使用Sentry进行错误追踪",
    },
    {
        "name": "compound-engineering",
        "repo": "https://github.com/EveryInc/compound-engineering-plugin",
        "description": "复合工程技能，集成多种工程工具和工作流",
    },
    {
        "name": "skill-seekers",
        "repo": "https://github.com/yusufkaraaslan/Skill_Seekers",
        "description": "技能搜索工具，帮助发现和安装新的AI技能",
    },
    {
        "name": "claude-code-tips",
        "repo": "https://github.com/ykdojo/claude-code-tips",
        "description": "Claude Code使用技巧和最佳实践，提升开发效率",
    },
    {
        "name": "plannotator",
        "repo": "https://github.com/backnotprop/plannotator",
        "description": "规划标注工具，可视化项目计划和任务流程",
    },
    {
        "name": "trail-of-bits-skills",
        "repo": "https://github.com/trailofbits/skills",
        "description": "Trail of Bits安全技能，代码安全审查和漏洞检测",
    },
    {
        "name": "oneredoak-workflows",
        "repo": "https://github.com/OneRedOak/claude-code-workflows",
        "description": "OneRedOak工作流技能，自动化开发工作流程",
    },
]


def run_cmd(cmd, cwd=None):
    """执行命令并返回结果"""
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def clone_repo(repo_url, dest_dir):
    """克隆仓库到指定目录"""
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
    """在仓库中查找SKILL.md文件"""
    skill_files = []
    for root, dirs, files in os.walk(repo_dir):
        for f in files:
            if f.lower() == "skill.md":
                skill_files.append(Path(root) / f)
    return skill_files


def compute_hash(content):
    """计算内容hash"""
    if isinstance(content, str):
        content = content.encode("utf-8")
    return hashlib.sha256(content).hexdigest()


def register_to_db(conn, skill_name, description, skill_dir):
    """注册skill到数据库"""
    cur = conn.cursor()

    # 检查是否已存在
    cur.execute("SELECT id FROM skills WHERE name = ?", (skill_name,))
    existing = cur.fetchone()
    if existing:
        return f"  = 已存在，跳过"

    # 计算content_hash
    skill_file = skill_dir / "SKILL.md"
    content_hash = ""
    if skill_file.exists():
        content_hash = compute_hash(skill_file.read_bytes())

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
        "import", skill_dir.name,
        str(skill_dir), content_hash,
        now_ms, now_ms, now_ms
    ))

    # 添加标签
    for tag in ["new", "community"]:
        cur.execute(
            "INSERT OR IGNORE INTO skill_tags (skill_id, tag) VALUES (?, ?)",
            (skill_id, tag)
        )

    return f"  + 已注册"


def link_to_project(skill_name):
    """链接到项目目录"""
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
            return f"    ⚠ 权限不足，已复制"
    except Exception as e:
        try:
            shutil.copytree(source, target)
            return f"    ⚠ 已复制代替"
        except:
            return f"    ✗ 链接失败"


def main():
    print("=" * 70)
    print("批量安装14个新Skill")
    print("=" * 70)

    # 准备目录
    TEMP_CLONE_DIR.mkdir(parents=True, exist_ok=True)
    CENTRAL_SKILLS_DIR.mkdir(parents=True, exist_ok=True)
    PROJECT_SKILLS_DIR.mkdir(parents=True, exist_ok=True)

    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # 统计
    success_count = 0
    fail_count = 0
    skipped_count = 0
    results = []

    for skill in SKILLS_TO_INSTALL:
        print(f"\n{'-'*70}")
        print(f"安装: {skill['name']}")
        print(f"仓库: {skill['repo']}")

        # 克隆仓库
        repo_dir = TEMP_CLONE_DIR / skill['name']
        if not clone_repo(skill['repo'], repo_dir):
            fail_count += 1
            results.append({"name": skill['name'], "status": "FAIL", "reason": "克隆失败"})
            continue

        # 查找SKILL.md
        skill_files = find_skill_files(repo_dir)
        print(f"  找到 {len(skill_files)} 个 SKILL.md")

        if len(skill_files) == 0:
            # 如果没有SKILL.md，创建一个基础的
            print(f"  未找到SKILL.md，创建基础版本")
            target_skill_dir = CENTRAL_SKILLS_DIR / skill['name']
            target_skill_dir.mkdir(parents=True, exist_ok=True)
            skill_file = target_skill_dir / "SKILL.md"
            skill_file.write_text(f"""---
name: {skill['name']}
description: {skill['description']}
tags: community
always: false
---

# {skill['name']}

{skill['description']}

**GitHub**: {skill['repo']}
""", encoding="utf-8")
        else:
            # 复制skill文件到central目录
            for sf in skill_files:
                skill_name_from_file = sf.parent.name
                if skill_name_from_file == skill['name']:
                    target_skill_dir = CENTRAL_SKILLS_DIR / skill['name']
                else:
                    target_skill_dir = CENTRAL_SKILLS_DIR / skill_name_from_file

                target_skill_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(sf, target_skill_dir / "SKILL.md")

                # 复制其他相关文件
                for item in sf.parent.iterdir():
                    if item != sf and item.name != "__pycache__":
                        if item.is_file():
                            shutil.copy2(item, target_skill_dir / item.name)
                        elif item.is_dir():
                            shutil.copytree(item, target_skill_dir / item.name, dirs_exist_ok=True)

                print(f"  复制: {sf} -> {target_skill_dir}")

        # 注册到数据库
        target_skill_dir = CENTRAL_SKILLS_DIR / skill['name']
        reg_result = register_to_db(conn, skill['name'], skill['description'], target_skill_dir)
        print(f"  数据库: {reg_result}")

        if "已存在" in reg_result:
            skipped_count += 1
            results.append({"name": skill['name'], "status": "SKIP", "reason": "已存在"})
        elif "已注册" in reg_result:
            success_count += 1
            results.append({"name": skill['name'], "status": "OK"})

        # 链接到项目
        link_result = link_to_project(skill['name'])
        print(link_result)

        # 清理临时克隆目录
        shutil.rmtree(repo_dir, ignore_errors=True)

    conn.commit()
    conn.close()

    # 清理临时目录
    shutil.rmtree(TEMP_CLONE_DIR, ignore_errors=True)

    # 输出报告
    print("\n" + "=" * 70)
    print("安装报告")
    print("=" * 70)
    print(f"成功: {success_count}")
    print(f"跳过: {skipped_count}")
    print(f"失败: {fail_count}")
    print("-" * 70)
    for r in results:
        status_icon = {"OK": "✓", "SKIP": "=", "FAIL": "✗"}[r['status']]
        reason = r.get('reason', '')
        print(f"  {status_icon} {r['name']} {reason}")

    # 验证数据库
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as cnt FROM skills")
    total = cur.fetchone()["cnt"]
    conn.close()
    print(f"\n数据库总技能数: {total}")


if __name__ == "__main__":
    main()
