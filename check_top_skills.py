import sqlite3

DB_PATH = r"C:\Users\biren\.skills-manager\skills-manager.db"
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

skills_to_check = [
    "planning-with-files", "superpowers", "code-review", 
    "webapp-testing", "code-simplifier", "ui-ux-pro-max", 
    "mcp-builder", "ralph-loop", "pptx", "skill-creator"
]

print("检查十大必装skill是否已安装：")
print("-" * 50)

for name in skills_to_check:
    cur.execute("SELECT name FROM skills WHERE name = ? OR name LIKE ?", (name, name + "%"))
    found = cur.fetchall()
    if found:
        print(f"{name:25s} → 已安装 ({', '.join([f[0] for f in found])})")
    else:
        print(f"{name:25s} → 未安装")

conn.close()
