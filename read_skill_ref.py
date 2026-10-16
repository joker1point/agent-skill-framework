"""读取技能目录内参考资料文件的工具（限定在技能根目录内，防越权）。

供 R1 实验的 retrieve 臂使用：agent 先用 load_skill 拿到 SKILL.md 索引，
再用本工具读取对应 references/*.md 文件（复现 dev-lessons 的真实检索链路）。
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

MAX_CHARS = 20000  # 长文件（如 misc.md ~3 万字符）截断，避免撑爆 token 预算


class ReadSkillRefTool:
    name = "read_skill_ref"
    description = (
        "读取指定技能目录下的参考资料文件（如 references/frontend-backend.md）。"
        "先用 load_skill 加载技能拿到索引与场景路由表，再据此读取对应文件。"
        "参数 skill_name：技能名（如 dev-lessons）；"
        "relative_path：相对于技能根的路径，必须以 'references/' 开头。"
    )
    parameters = {
        "type": "object",
        "properties": {
            "skill_name": {"type": "string", "description": "技能名，如 dev-lessons"},
            "relative_path": {
                "type": "string",
                "description": "文件相对路径，必须以 references/ 开头，如 references/frontend-backend.md",
            },
        },
        "required": ["skill_name", "relative_path"],
    }
    read_only = True

    def __init__(self, loader: Any):
        self.loader = loader

    def execute(self, skill_name: str, relative_path: str) -> str:
        if not relative_path.startswith("references/"):
            return "Error: relative_path 必须以 'references/' 开头。"
        base = Path(self.loader.skills_dir) / skill_name
        try:
            target = (base / relative_path).resolve()
            base_res = base.resolve()
            if base_res != target and base_res not in target.parents:
                return f"Error: 越权路径 {relative_path}（必须在技能目录内）。"
        except (OSError, ValueError) as e:
            return f"Error: 路径解析失败 {e}"
        if not target.exists():
            return f"Error: 文件不存在 {relative_path}"
        text = target.read_text(encoding="utf-8")
        if len(text) > MAX_CHARS:
            text = text[:MAX_CHARS] + f"\n...[已截断，原文件 {len(text)} 字符，请按需精读]"
        return text
