from pathlib import Path
from skills_loader import SkillsLoader
from load_skill_tool import LoadSkillTool


def test_skills_loader():
    skills_dir = Path(__file__).parent / "skills"
    loader = SkillsLoader(skills_dir)

    print("=" * 60)
    print("测试技能加载器")
    print("=" * 60)

    print("\n1. 列出所有技能:")
    skills = loader.list_skills()
    print(f"   可用技能: {skills}")

    print("\n2. 构建技能摘要:")
    summary = loader.build_skills_summary()
    print(summary)

    print("\n3. 获取技能内容 (weather):")
    content = loader.get_content("weather")
    print(content[:500] + "..." if len(content) > 500 else content)

    print("\n4. 获取技能内容 (github):")
    content = loader.get_content("github")
    print(content[:500] + "..." if len(content) > 500 else content)

    print("\n5. 获取不存在的技能:")
    content = loader.get_content("nonexistent")
    print(content)

    print("\n6. 获取 always 技能:")
    always_skills = loader.get_always_skills()
    print(f"   Always 技能: {always_skills}")


def test_load_skill_tool():
    skills_dir = Path(__file__).parent / "skills"
    loader = SkillsLoader(skills_dir)
    tool = LoadSkillTool(loader)

    print("\n" + "=" * 60)
    print("测试 LoadSkill 工具")
    print("=" * 60)

    print("\n工具名称:", tool.name)
    print("工具描述:", tool.description)
    print("工具参数:", tool.parameters)

    print("\n执行工具调用 (weather):")
    result = tool.execute("weather")
    print(result[:300] + "..." if len(result) > 300 else result)


if __name__ == "__main__":
    test_skills_loader()
    test_load_skill_tool()
    print("\n✓ 所有测试通过!")