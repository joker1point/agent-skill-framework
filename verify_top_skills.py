import sqlite3

DB_PATH = r"C:\Users\biren\.skills-manager\skills-manager.db"
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

TOP_SKILLS = [
    ("planning-with-files", "规划与文件"),
    ("superpowers", "超级能力套件"),
    ("code-review", "代码审查"),
    ("webapp-testing", "Web应用测试"),
    ("code-simplifier", "代码简化"),
    ("ui-ux-pro-max", "UI UX设计"),
    ("mcp-builder", "MCP构建器"),
    ("ralph-loop", "循环改进"),
    ("pptx-generator", "PPTX生成"),
    ("skill-creator", "技能创建器"),
]

print("十大必装Skill分类结果：")
print("=" * 70)
print(f"{'序号':<4} {'Skill':<25} {'中文名称':<12} {'分类':<12} {'来源':<6}")
print("-" * 70)

for i, (name, cn_name) in enumerate(TOP_SKILLS, 1):
    cur.execute("SELECT id FROM skills WHERE name = ?", (name,))
    skill_row = cur.fetchone()
    if skill_row:
        skill_id = skill_row["id"]
        cur.execute("SELECT category_label FROM skill_categories WHERE skill_id = ?", (skill_id,))
        cat_row = cur.fetchone()
        category = cat_row["category_label"] if cat_row else "未分类"
        
        cur.execute("SELECT description FROM skills WHERE id = ?", (skill_id,))
        desc = cur.fetchone()["description"]
        source = "官方" if "官方" in desc else "社区"
        
        print(f"{i:<4} {name:<25} {cn_name:<12} {category:<12} {source:<6}")
    else:
        print(f"{i:<4} {name:<25} {cn_name:<12} {'未安装':<12}")

conn.close()
