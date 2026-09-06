import sqlite3
import time

DB_PATH = r"C:\Users\biren\.skills-manager\skills-manager.db"

ASSIGNMENTS = {
    "研究分析": ["arxiv-watcher", "citation-manager"],
    "Agent系统": ["caveman", "model-usage", "team-ops"],
    "开发运维": ["cnb-skill"],
    "文档处理": ["file-diff-checker", "guizang-ppt-skill"],
    "金融数据": ["install-futu-opend"],
    "效率工具": ["material-organizer", "peekaboo", "trello", "workrally"],
    "写作出版": ["resume-assistant"],
    "出行生活": ["sino-drug-instructions-search"],
    "技能管理": ["mcporter-2"],
    "通讯协作": ["wacli"],
}

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("SELECT id, name FROM skills")
name_to_id = {row["name"]: row["id"] for row in cur.fetchall()}

cur.execute("SELECT id, name FROM scenarios")
preset_name_to_id = {row["name"]: row["id"] for row in cur.fetchall()}

now_ms = int(time.time() * 1000)
total_linked = 0

for preset_name, skill_names in ASSIGNMENTS.items():
    scenario_id = preset_name_to_id.get(preset_name)
    if not scenario_id:
        print(f"WARNING: Preset '{preset_name}' not found")
        continue

    for skill_name in skill_names:
        skill_id = name_to_id.get(skill_name)
        if skill_id:
            cur.execute(
                "INSERT OR IGNORE INTO scenario_skills (scenario_id, skill_id, added_at, sort_order) VALUES (?, ?, ?, ?)",
                (scenario_id, skill_id, now_ms, 999),
            )
            total_linked += 1
        else:
            print(f"WARNING: Skill '{skill_name}' not found")

conn.commit()

cur.execute("SELECT COUNT(DISTINCT skill_id) as c FROM scenario_skills")
assigned = cur.fetchone()["c"]
cur.execute("SELECT COUNT(*) as c FROM skills")
total_skills = cur.fetchone()["c"]
cur.execute("SELECT COUNT(*) as c FROM scenarios")
total_presets = cur.fetchone()["c"]
cur.execute("""SELECT name FROM skills WHERE id NOT IN (SELECT skill_id FROM scenario_skills) ORDER BY name""")
remaining = [r["name"] for r in cur.fetchall()]

conn.close()

print(f"Additional skills linked: {total_linked}")
print(f"Total assigned: {assigned}/{total_skills}")
print(f"Total presets: {total_presets}")
print(f"Remaining unassigned: {len(remaining)}")
if remaining:
    print(f"  {', '.join(remaining)}")
