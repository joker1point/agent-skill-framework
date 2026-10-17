import os
from pathlib import Path
from skill_linker import SkillLinker


def test_skill_linker():
    skills_repo = Path("%USERPROFILE%/GitHub/baoyu-skills")
    project_root = Path("%USERPROFILE%/Documents/trae_projects/0-1agent")

    linker = SkillLinker(skills_repo, project_root)

    print("=" * 60)
    print("测试 Skill 软链接管理工具")
    print("=" * 60)

    print("\n1. 创建软链接 (weather):")
    result = linker.link_skill("weather")
    print(f"   {result}")

    print("\n2. 创建软链接 (github):")
    result = linker.link_skill("github")
    print(f"   {result}")

    print("\n3. 创建软链接 (summarize):")
    result = linker.link_skill("summarize")
    print(f"   {result}")

    print("\n4. 设置 Agent 入口:")
    result = linker.setup_agent_entry()
    print(f"   {result}")

    print("\n5. 列出所有链接:")
    links = linker.list_links()
    if links:
        for link in links:
            status = "✓" if link["exists"] else "✗"
            link_type = "🔗" if link["type"] == "symlink" else "📁"
            print(f"   {status} {link_type} {link['name']}")
            print(f"      类型: {link['type']}")
            print(f"      路径: {link['link_path']}")
            print(f"      目标: {link['target_path']}")
    else:
        print("   暂无链接")

    print("\n6. 验证软链接内容:")
    weather_skill = project_root / ".agents" / "skills" / "weather" / "SKILL.md"
    if weather_skill.exists():
        content = weather_skill.read_text(encoding="utf-8")[:200]
        print(f"   weather/SKILL.md 内容:\n   {content}...")
    else:
        print("   Error: 文件不存在")

    print("\n7. 删除链接 (summarize):")
    result = linker.unlink_skill("summarize")
    print(f"   {result}")

    print("\n8. 更新技能 (github):")
    result = linker.update_skill("github")
    print(f"   {result}")

    print("\n9. 创建新 Skill:")
    result = linker.create_skill("my-custom-skill", "自定义技能", "custom, demo")
    print(f"   {result}")

    print("\n10. 同步所有技能:")
    result = linker.sync_all()
    print(f"   {result}")

    print("\n11. 列出最终链接:")
    links = linker.list_links()
    for link in links:
        status = "✓" if link["exists"] else "✗"
        link_type = "🔗" if link["type"] == "symlink" else "📁"
        print(f"   {status} {link_type} {link['name']}")


if __name__ == "__main__":
    test_skill_linker()
    print("\n✓ 所有测试完成!")