import sqlite3
import uuid
import time

DB_PATH = r"C:\Users\biren\.skills-manager\skills-manager.db"

NEW_PRESETS = {
    "tencent-eco": {
        "label": "腾讯生态",
        "description": "腾讯云/文档/会议/问卷等产品工具集",
        "skills": [
            "andonq", "cloudq", "cloudbase", "cos-vectors", "edgeone",
            "edgeone-pages-deploy", "migraq", "qcc-company", "smart-page",
            "skills-security-check", "tapd-openapi", "tencent-campus-recruit",
            "tencent-docs", "tencent-esign-contract", "tencent-esign-contract-2",
            "tencent-meeting-mcp", "tencent-meeting-skill", "tencent-musician-skills",
            "tencent-news", "tencent-ssv-techforgood", "tencent-survey",
            "tencent-survey-2", "tencent-yuanbao-standard-search", "tencent-yunzhi",
            "tencentcloud-cls", "tencentcloud-cos", "tencentos-expert",
            "tencentmap-lbs-skill", "cloud-upload-backup",
        ],
    },
    "mobile-dev": {
        "label": "移动开发",
        "description": "Android/iOS/Flutter/小程序开发工具集",
        "skills": [
            "android-cli", "android-native-dev", "flutter-dev",
            "ios-application-dev", "wechat-miniprogram",
            "tdesign-miniprogram", "skyline", "shader-dev",
        ],
    },
    "education": {
        "label": "教育学习",
        "description": "学术翻译/辅导/备考/课程创作工具集",
        "skills": [
            "academic-translation", "academic-tutor", "education",
            "english-exam-writing-reviewer", "english-intensive-reader",
            "knowledge-framework-builder", "open-lesson", "study-planner",
            "teachany", "tutor-skills", "boss-skills",
        ],
    },
    "writing": {
        "label": "写作出版",
        "description": "小说/网文/公众号/文案写作工具集",
        "skills": [
            "novel", "novel-writing", "open-novel-writing", "khazix-writer",
            "charity-writing-assistant", "content-factory", "content-ops",
            "content-repurposer", "content-repurposer-2", "x-longform-post",
            "ecommerce-copywriter", "podcast-ops", "wechat-article-search",
            "wechat-publisher", "wechat-publisher-2",
        ],
    },
    "productivity": {
        "label": "效率工具",
        "description": "笔记/任务/日程/知识管理工具集",
        "skills": [
            "apple-notes", "apple-reminders", "caldav-calendar", "things-mac",
            "goal-tracker", "habit-tracker", "healthcheck", "plan-tracker",
            "note-organizer", "obsidian", "llm-wiki", "qmd", "notebooklm-studio",
            "tmux", "handoff", "task-alignment", "task-implement", "summarize",
            "jinshuju",
        ],
    },
    "agent-system": {
        "label": "Agent系统",
        "description": "Agent人设/团队编排/能力进化工具集",
        "skills": [
            "agent-browser-core", "agent-mbti", "agent-team-orchestration",
            "another_them", "anti-distill", "capability-evolver", "cangjie-skill",
            "darwin-skill", "nuwa-skill", "persona-switch", "yourself-skill",
            "colleague-skill", "impeccable", "prompt-engineering-expert",
            "zoom-out", "grill-me", "oracle", "idea-validator",
            "the-entrepreneurship-handbook", "openclaw-assets-to-workbuddy",
            "github", "github-ai-trends",
        ],
    },
    "ecommerce": {
        "label": "电商运营",
        "description": "电商搜索/支付/SCRM/选品工具集",
        "skills": [
            "admapix", "cn-ecommerce-search", "ecomseer", "maishou",
            "mtunion-product-ai-guide", "ozon-1688-uploader", "shopify-admin-api",
            "vip-skill", "wechatpay-basic-payment", "wechatpay-product-coupon",
            "wecom-weisheng-scrm", "wecom-weisheng-scrm-2",
        ],
    },
    "travel-transport": {
        "label": "出行交通",
        "description": "火车/飞机/美团/旅行规划工具集",
        "skills": [
            "12306-train-assistant", "airchina-travel-assistant",
            "aviationstack-flight-tracker", "flight-tracker", "flights",
            "flyai", "globepilot-ai-agent-2", "aviation-weather",
            "meituan-coupon-workbuddy", "meituan-huisheng-coupon",
            "travel-planning",
        ],
    },
    "av-media": {
        "label": "音视频",
        "description": "语音转写/视频生成/图片生成工具集",
        "skills": [
            "openai-whisper", "openai-whisper-api", "remotion-video-toolkit",
            "video-frames", "songsee", "sag", "libtv-skill",
            "nano-banana-pro", "gifgrep", "nano-pdf",
        ],
    },
    "marketing": {
        "label": "营销增长",
        "description": "营销/销售/SEO/竞品分析工具集",
        "skills": [
            "marketing-skills", "growth-engine", "conversion-ops",
            "competitorsmart", "seo-ops", "sales-pipeline", "sales-playbook",
            "revenue-intelligence", "outbound-engine", "promo-creator-skills",
            "yt-competitive-analysis", "xurl",
        ],
    },
    "cloud-storage": {
        "label": "云存储阅读",
        "description": "网盘/云文档/微信读书/知识库工具集",
        "skills": [
            "baidu-drive", "bdpan-storage", "weiyun", "kdocs", "kdocs-2",
            "lexiang-knowledge-base", "ima-skills", "weread-skills",
            "weread-skills-2", "tencent-yunzhi",
        ],
    },
    "devops-infra": {
        "label": "开发运维",
        "description": "部署/性能/测试/诊断工具集",
        "skills": [
            "github-pages-auto-deploy", "cli-anything-hub", "api-gateway",
            "cloudflare-worker-builder", "shippage", "static-app",
            "web-performance-audit", "crash-expert-skill", "diagnose",
            "python-performance-optimization", "python-testing-patterns",
            "fintech-engineer", "finance-ops", "landing-page-generator",
            "product-showcase-site", "redesign-existing-projects",
            "awesome-design-md", "deck-generator",
        ],
    },
    "email-extra": {
        "label": "邮件增强",
        "description": "邮件收发/日程/Workspace工具集",
        "skills": [
            "email-daily-summary", "email-skill-2", "gog", "himalaya",
            "imap-smtp-email", "imap-smtp-email-2", "porteden-email", "qq-email",
            "imsg",
        ],
    },
    "browser-extra": {
        "label": "浏览器扩展",
        "description": "Playwright/浏览器自动化/响应式测试工具集",
        "skills": [
            "browser-cash", "browserwing", "clawbrowser",
            "playwright-browser-automation", "playwright-scraper-skill",
            "stagehand-browser-cli", "responsiveness-check",
        ],
    },
    "search-news": {
        "label": "搜索资讯",
        "description": "多引擎搜索/新闻/趋势工具集",
        "skills": [
            "web-search-exa", "multi-search-engine", "aihot",
            "tech-news-digest", "blogwatcher", "github-trending-cn",
        ],
    },
    "legal-finance": {
        "label": "法律金融",
        "description": "合同/法律/基金/金融数据工具集",
        "skills": [
            "legal-logic-analysis", "fadada-document-sign",
            "charity-finance-assistant", "lingxi-financialsearch-skill",
            "neodata-financial-search", "football-bayes", "yingmi-skill",
        ],
    },
}

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("SELECT id, name FROM skills")
name_to_id = {row["name"]: row["id"] for row in cur.fetchall()}

cur.execute("SELECT MAX(sort_order) as max_sort FROM scenarios")
max_sort = cur.fetchone()["max_sort"] or 0

now_ms = int(time.time() * 1000)
report = []
total_linked = 0
total_missing = 0

for sort_idx, (preset_id, preset) in enumerate(NEW_PRESETS.items(), start=max_sort + 1):
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
print(f"New presets created: {len(NEW_PRESETS)}")
print(f"Total linked: {total_linked}")
print(f"Total missing: {total_missing}")
print("=" * 60)
for r in report:
    status = "OK" if not r["missing"] else "PARTIAL"
    print(f"\n[{status}] {r['preset']} - {r['linked']} skills linked")
    if r["missing"]:
        print(f"  Missing: {', '.join(r['missing'])}")
