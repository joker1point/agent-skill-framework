from __future__ import annotations


class LoadSkillTool:
    name = "load_skill"
    description = "加载指定技能的详细知识内容，在回答相关问题前调用"
    read_only = True

    def __init__(self, skills_loader):
        self._loader = skills_loader

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "skill_name": {
                    "type": "string",
                    "description": "技能名称，必须是系统提示中列出的可用技能之一"
                }
            },
            "required": ["skill_name"]
        }

    def execute(self, skill_name: str) -> str:
        print(f"[加载技能]: {skill_name}")
        return self._loader.get_content(skill_name)