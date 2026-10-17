import os
import sqlite3
import json
import re

DB_PATH = os.path.expandvars(r"%USERPROFILE%\.skills-manager\skills-manager.db")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute("SELECT id, name, description FROM skills ORDER BY name")
rows = cur.fetchall()
skills = [dict(r) for r in rows]
conn.close()

CATEGORIES = {
    "dev-tools": {
        "label": "开发工具",
        "keywords": ["dev", "code", "cli", "flutter", "react", "android", "frontend",
                     "fullstack", "shader", "tdd", "mcp-builder", "mcporter", "skill-creator",
                     "skill-scanner", "skill-vetter", "setup-pre-commit", "cangjie", "cnb-skill",
                     "flutter", "native-dev", "miniprogram", "static-app", "api-gateway",
                     "capability-evolver", "task-implement", "task-alignment", "handoff",
                     "agent-team", "tdd", "fintech-engineer"],
    },
    "doc-suite": {
        "label": "文档处理",
        "keywords": ["docx", "pdf", "xlsx", "pptx", "markdown", "md-to", "markitdown",
                     "pdfkit", "qmd", "minimax-docx", "minimax-pdf", "minimax-xlsx",
                     "citation", "file-diff", "document"],
    },
    "web-browser": {
        "label": "浏览器与网页",
        "keywords": ["browser", "web-scraper", "web-access", "web-search", "web-deploy",
                     "clawbrowser", "browserwing", "smooth-browser", "stealth-browser",
                     "browser-use", "browser-cash", "agent-browser", "xurl", "peekaboo"],
    },
    "ai-research": {
        "label": "AI与研究",
        "keywords": ["research", "arxiv", "perplexity", "tavily", "autoresearch",
                     "deep-research", "llm-wiki", "paper-quick", "jiaozhen", "factcheck",
                     "diagnose", "oracle", "model-usage", "agent-mbti", "capability"],
    },
    "design-creative": {
        "label": "设计与创意",
        "keywords": ["design", "figma", "canvas", "diagram", "infographic", "gif",
                     "sticker", "excalidraw", "brand", "awesome-design", "deck-generator",
                     "nano-banana", "openai-image", "songsee", "zoom-out", "smart-page",
                     "caveman", "darwin-skill"],
    },
    "comm-suite": {
        "label": "邮件与通讯",
        "keywords": ["email", "gmail", "mail", "imsg", "dingtalk", "lark", "wecom",
                     "qq-email", "agentmail", "himalaya", "imap", "smtp", "porteden",
                     "blogwatcher"],
    },
    "deploy-cloud": {
        "label": "部署与云服务",
        "keywords": ["deploy", "vercel", "netlify", "cloudflare", "html-deploy",
                     "web-deploy", "cloudbase", "edgeone", "tencentcloud", "cloudq",
                     "shippage", "netlify"],
    },
    "finance-data": {
        "label": "金融与数据",
        "keywords": ["stock", "finance", "futu", "market", "earnings", "westock",
                     "macro", "football-bayes", "conversion-ops", "growth-engine",
                     "outbound-engine", "sales", "competitorsmart", "seo"],
    },
    "content-creation": {
        "label": "内容创作",
        "keywords": ["content", "novel", "writer", "video", "blog", "podcast",
                     "humanizer", "khazix", "guizang", "wechat-article", "x-longform",
                     "my-novel", "novel-writing", "open-novel", "fbs-bookwriter", "fbs_bookwriter",
                     "video-script", "video-frames", "news-summary", "tech-news",
                     "aihot", "github-trending", "github-ai", "tencent-news"],
    },
    "travel-lifestyle": {
        "label": "出行与生活",
        "keywords": ["weather", "travel", "flight", "12306", "didi", "ctrip",
                     "airbnb", "airchina", "aviation", "meituan", "travel-cn",
                     "travel-planning", "tencent-weather", "habit-tracker", "goal-tracker",
                     "study-planner", "open-lesson", "tutor", "academic", "education",
                     "football", "grill", "health", "plan-tracker"],
    },
    "wechat-social": {
        "label": "微信与社交",
        "keywords": ["wechat", "weixin", "weread", "ima-skills", "kdocs", "tencent-docs",
                     "jinshuju", "tencent-survey", "qq", "weiyun", "baidu-drive",
                     "bdpan", "obsidian", "note", "apple-notes", "apple-reminders",
                     "things-mac", "caldav", "trello", "workrally", "team-ops",
                     "colleague", "vip-skill", "yourself", "nuwa", "yingmi",
                     "persona-switch", "idea-validator", "teachany", "tutor-skills",
                     "resume", "anti-distill", "impeccable", "material-organizer",
                     "crash-expert", "tencentos", "tapd", "qcc", "tencent-yunzhi"],
    },
    "search-tools": {
        "label": "搜索工具",
        "keywords": ["search", "tavily", "perplexity", "web-search-exa", "migraq",
                     "gifgrep", "flyai", "gog", "wacli", "libtv", "install-futu",
                     "mac", "tmux", "sag", "skyline", "gog", "migraq"],
    },
}

def classify(skill_name, description):
    name_lower = skill_name.lower()
    desc_lower = (description or "").lower()
    for cat_id, cat in CATEGORIES.items():
        for kw in cat["keywords"]:
            if kw in name_lower or kw in desc_lower:
                return cat_id
    return "other"

result = {}
uncategorized = []

for s in skills:
    cat = classify(s["name"], s["description"])
    if cat == "other":
        uncategorized.append(s["name"])
    else:
        result.setdefault(cat, []).append(s["name"])

print("=" * 60)
print(f"Total skills: {len(skills)}")
print(f"Categorized: {len(skills) - len(uncategorized)}")
print(f"Uncategorized: {len(uncategorized)}")
print("=" * 60)

for cat_id, cat in CATEGORIES.items():
    items = result.get(cat_id, [])
    print(f"\n## {cat['label']} ({cat_id}) — {len(items)} skills")
    for name in items:
        print(f"  - {name}")

if uncategorized:
    print(f"\n## 未分类 — {len(uncategorized)} skills")
    for name in uncategorized:
        print(f"  - {name}")
