import os
import sqlite3
import uuid
import time
import json

DB_PATH = os.path.expandvars(r"%USERPROFILE%\.skills-manager\skills-manager.db")

PRESETS = {
    "web-dev": {
        "label": "Web开发",
        "description": "Web/前端/全栈开发工具集",
        "skills": [
            "frontend-dev", "fullstack-dev", "react-native-dev",
            "vercel-react-best-practices", "design-taste-frontend",
            "tdd", "setup-pre-commit",
            "vercel-deploy", "netlify-deploy", "html-deploy",
            "cloudflare", "web-deploy", "web-deploy-github",
        ],
    },
    "docs": {
        "label": "文档处理",
        "description": "文档生成与转换工具集",
        "skills": [
            "docx", "pdf", "xlsx", "pptx-generator",
            "markitdown-skill", "md-to-pdf-cjk", "pdfkit-py",
            "minimax-docx", "minimax-pdf", "minimax-xlsx",
        ],
    },
    "research": {
        "label": "研究分析",
        "description": "深度研究与事实核查工具集",
        "skills": [
            "deep-research", "autoresearch", "arxiv-reader",
            "perplexity", "tavily", "paper-quick-reader",
            "jiaozhen-factcheck", "market-researcher",
        ],
    },
    "content": {
        "label": "内容创作",
        "description": "内容创作与写作工具集",
        "skills": [
            "content-creator", "novel-writer", "fbs-bookwriter",
            "fbs_bookwriter", "humanizer", "video-script-gen",
            "wechat-article-pro", "news-summary",
            "github-trending-cn", "my-novel-writer",
        ],
    },
    "browser": {
        "label": "浏览器自动化",
        "description": "浏览器控制与网页抓取工具集",
        "skills": [
            "browser", "browser-use", "smooth-browser",
            "stealth-browser", "web-scraper", "web-access",
        ],
    },
    "comm": {
        "label": "通讯协作",
        "description": "邮件与即时通讯工具集",
        "skills": [
            "gmail", "email-skill", "dingtalk-unified",
            "lark-unified", "wecom-unified", "agentmail",
        ],
    },
    "finance": {
        "label": "金融数据",
        "description": "股票行情与金融分析工具集",
        "skills": [
            "stock-analysis", "us-stock-analysis", "futuapi",
            "earnings-tracker", "macro-monitor",
            "westockdata", "stock-analyzer",
        ],
    },
    "design": {
        "label": "设计创意",
        "description": "设计制图与创意工具集",
        "skills": [
            "figma", "canvas-design", "excalidraw-diagram",
            "infographic-maker", "gif-sticker-maker",
            "openai-image-gen", "brand-guidelines",
            "data-visualization",
        ],
    },
    "lifestyle": {
        "label": "出行生活",
        "description": "天气出行与生活服务工具集",
        "skills": [
            "weather", "12306", "travel-cn",
            "airbnb", "didi-ride-skill",
            "meituan-travel", "ctrip-wendao",
            "tencent-weather",
        ],
    },
    "skill-mgmt": {
        "label": "技能管理",
        "description": "Skill 创建与管理工具集",
        "skills": [
            "skill-creator", "skill-scanner", "skill-vetter",
            "mcp-builder", "mcporter",
        ],
    },
}

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("SELECT id, name FROM skills")
name_to_id = {}
for row in cur.fetchall():
    name_to_id[row["name"]] = row["id"]

now_ms = int(time.time() * 1000)
report = []
total_linked = 0
total_missing = 0

for sort_idx, (preset_id, preset) in enumerate(PRESETS.items(), start=1):
    scenario_id = str(uuid.uuid4())
    cur.execute(
        "INSERT INTO scenarios (id, name, description, icon, sort_order, created_at, updated_at) VALUES (?, ?, ?, NULL, ?, ?, ?)",
        (scenario_id, preset["label"], preset["description"], sort_idx, now_ms, now_ms),
    )

    linked = []
    missing = []
    for skill_idx, skill_name in enumerate(preset["skills"]):
        skill_id = name_to_id.get(skill_name)
        if skill_id:
            cur.execute(
                "INSERT OR IGNORE INTO scenario_skills (scenario_id, skill_id, added_at, sort_order) VALUES (?, ?, ?, ?)",
                (scenario_id, skill_id, now_ms, skill_idx),
            )
            linked.append(skill_name)
        else:
            missing.append(skill_name)

    total_linked += len(linked)
    total_missing += len(missing)
    report.append({
        "preset": preset["label"],
        "linked": len(linked),
        "missing": missing,
    })

conn.commit()
conn.close()

print("=" * 60)
print(f"Preset creation complete!")
print(f"Total linked: {total_linked}")
print(f"Total missing: {total_missing}")
print("=" * 60)
for r in report:
    status = "OK" if not r["missing"] else "PARTIAL"
    print(f"\n[{status}] {r['preset']} — {r['linked']} skills linked")
    if r["missing"]:
        print(f"  Missing: {', '.join(r['missing'])}")
