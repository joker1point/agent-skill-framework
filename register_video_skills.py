"""
注册7个视频制作新skill到数据库，并创建"视频制作"预设。
同时将新skill链接到项目的 .agents/skills/ 目录。
"""
import sqlite3
import uuid
import time
import hashlib
import json
from pathlib import Path

DB_PATH = os.path.expandvars(r"%USERPROFILE%\.skills-manager\skills-manager.db")
CENTRAL_SKILLS_DIR = Path(os.path.expandvars(r"%USERPROFILE%\.skills-manager\skills"))
PROJECT_SKILLS_DIR = Path(os.path.expandvars(r"%USERPROFILE%\Documents\trae_projects\0-1agent\.agents\skills"))

NEW_SKILLS = [
    {
        "name": "moneyprinterturbo",
        "description": "一键生成短视频：输入主题词自动拼接免费图库素材+配音+字幕，输出1080p视频。Agent自主制片，无需手动剪辑。星标之王91.9K星。",
        "source_type": "local",
        "source_ref": "https://github.com/harry0703/MoneyPrinterTurbo",
    },
    {
        "name": "opencut-editor",
        "description": "开源版剪映：浏览器内跑的时间线剪辑器，本地处理免费无水印。手动剪辑已有素材，非AI生成。59.3K星。",
        "source_type": "local",
        "source_ref": "https://github.com/OpenCut-app/OpenCut",
    },
    {
        "name": "open-generative-ai",
        "description": "生成工作室：统一界面接入200+图像与视频模型。从零生成画面，手动选择模型和参数。注意默认走MuAPI云端网关需付费key。20.6K星。",
        "source_type": "local",
        "source_ref": "https://github.com/Anil-matcha/Open-Generative-AI",
    },
    {
        "name": "openmontage",
        "description": "让Claude Code/Cursor变成会拍片的制片人。无GUI，纯Agent驱动，直接在代码编辑器里完成视频制片全流程。16.4K星。",
        "source_type": "local",
        "source_ref": "https://github.com/calesthio/OpenMontage",
    },
    {
        "name": "vimax",
        "description": "把想法、剧本甚至整本小说变成多镜头叙事视频。Agent自主制片，AI生成画面，来自港大HKUDS。10.6K星。",
        "source_type": "local",
        "source_ref": "https://github.com/HKUDS/ViMax",
    },
    {
        "name": "toonflow",
        "description": "专注把小说变成AI短剧。Agent自主制片，AI生成画面，剧情化叙事专精。10.4K星。",
        "source_type": "local",
        "source_ref": "https://github.com/HBAI-Ltd/Toonflow-app",
    },
    {
        "name": "palmier-pro",
        "description": "macOS原生剪辑器：把编辑、生成式AI和Agent放进同一条时间线。手动剪辑+AI生成混合模式。YC S24，8.5K星。",
        "source_type": "local",
        "source_ref": "https://github.com/palmier-io/palmier-pro",
    },
]

VIDEO_PRESET = {
    "label": "视频制作",
    "description": "视频剪辑、AI生成、Agent制片的完整工具集（手动剪辑→生成工作室→Agent自主制片）",
    "skills": [s["name"] for s in NEW_SKILLS],
}

def compute_content_hash(skill_dir: Path) -> str:
    """计算SKILL.md文件的hash"""
    skill_file = skill_dir / "SKILL.md"
    if skill_file.exists():
        return hashlib.sha256(skill_file.read_bytes()).hexdigest()
    return ""

def link_to_project(skill_name: str):
    """将skill从central目录链接到项目的.agents/skills/目录"""
    source = CENTRAL_SKILLS_DIR / skill_name
    target = PROJECT_SKILLS_DIR / skill_name

    if not source.exists():
        return f"  Warning: source not found: {source}"

    # 如果已存在，先删除
    if target.exists():
        import shutil
        if target.is_symlink():
            target.unlink()
        else:
            shutil.rmtree(target)

    # 尝试创建符号链接，失败则复制
    try:
        import os
        if os.name == "nt":
            import subprocess
            cmd = f'mklink /D "{target}" "{source}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                import shutil
                shutil.copytree(source, target)
                return f"  Copied (symlink denied): {skill_name}"
        else:
            os.symlink(source, target)
        return f"  Symlinked: {skill_name}"
    except Exception as e:
        import shutil
        try:
            shutil.copytree(source, target)
            return f"  Copied: {skill_name}"
        except Exception as e2:
            return f"  Error: {e2}"


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # 检查已有skills
    cur.execute("SELECT name FROM skills")
    existing_names = {row["name"] for row in cur.fetchall()}

    now_ms = int(time.time() * 1000)
    registered = []
    skipped = []

    for skill in NEW_SKILLS:
        if skill["name"] in existing_names:
            skipped.append(skill["name"])
            continue

        skill_dir = CENTRAL_SKILLS_DIR / skill["name"]
        content_hash = compute_content_hash(skill_dir)
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
            skill_id, skill["name"], skill["description"],
            skill["source_type"], skill["source_ref"],
            str(skill_dir), content_hash,
            now_ms, now_ms, now_ms
        ))

        # 添加标签
        for tag in ["video", "video-production", "ai-generation"]:
            cur.execute(
                "INSERT OR IGNORE INTO skill_tags (skill_id, tag) VALUES (?, ?)",
                (skill_id, tag)
            )

        registered.append(skill["name"])

    # 创建视频制作预设
    cur.execute("SELECT id FROM scenarios WHERE name = ?", (VIDEO_PRESET["label"],))
    existing_preset = cur.fetchone()

    if existing_preset:
        scenario_id = existing_preset["id"]
        cur.execute("DELETE FROM scenario_skills WHERE scenario_id = ?", (scenario_id,))
        print(f"Updated existing preset: {VIDEO_PRESET['label']}")
    else:
        scenario_id = str(uuid.uuid4())
        cur.execute("SELECT MAX(sort_order) as max_sort FROM scenarios")
        max_sort = cur.fetchone()["max_sort"] or 0
        cur.execute("""
            INSERT INTO scenarios (id, name, description, icon, sort_order, created_at, updated_at)
            VALUES (?, ?, ?, NULL, ?, ?, ?)
        """, (scenario_id, VIDEO_PRESET["label"], VIDEO_PRESET["description"],
              max_sort + 1, now_ms, now_ms))
        print(f"Created new preset: {VIDEO_PRESET['label']}")

    # 获取所有skill的name→id映射
    cur.execute("SELECT id, name FROM skills")
    name_to_id = {row["name"]: row["id"] for row in cur.fetchall()}

    linked_skills = []
    missing_skills = []
    for idx, skill_name in enumerate(VIDEO_PRESET["skills"]):
        skill_id = name_to_id.get(skill_name)
        if skill_id:
            cur.execute("""
                INSERT OR IGNORE INTO scenario_skills (scenario_id, skill_id, added_at, sort_order)
                VALUES (?, ?, ?, ?)
            """, (scenario_id, skill_id, now_ms, idx))
            linked_skills.append(skill_name)
        else:
            missing_skills.append(skill_name)

    conn.commit()

    # 链接到项目目录
    print("\n=== Linking skills to project ===")
    for name in registered:
        result = link_to_project(name)
        print(result)

    # 输出报告
    print("\n" + "=" * 60)
    print("REGISTRATION REPORT")
    print("=" * 60)
    print(f"Registered: {len(registered)} skills")
    for name in registered:
        print(f"  + {name}")
    if skipped:
        print(f"Skipped (already exists): {len(skipped)}")
        for name in skipped:
            print(f"  = {name}")
    print(f"\nPreset: {VIDEO_PRESET['label']}")
    print(f"  Linked: {len(linked_skills)} skills")
    if missing_skills:
        print(f"  Missing: {missing_skills}")

    # 验证
    cur.execute("SELECT COUNT(*) as cnt FROM skills")
    total_skills = cur.fetchone()["cnt"]
    cur.execute("SELECT COUNT(*) as cnt FROM scenarios")
    total_scenarios = cur.fetchone()["cnt"]
    print(f"\nDatabase totals: {total_skills} skills, {total_scenarios} scenarios")

    conn.close()


if __name__ == "__main__":
    main()
