from __future__ import annotations
import os
import time
from pathlib import Path
from typing import Optional, Tuple

from openai import OpenAI

from skills_loader import SkillsLoader


class RealAgentExecutor:
    """真实 agent 执行器: 调用 LLM API 执行评估 prompt。

    通过将 skill 内容注入 system prompt 实现 "with_skill" 配置;
    baseline 配置不注入 skill, 只用基础 system prompt。
    """

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        skills_dir: Path,
        max_tokens: int = 1024,
        temperature: float = 0.0,
    ):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.skills_dir = skills_dir
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.loader = SkillsLoader(skills_dir)

    def _build_system_prompt(self, skill_name: Optional[str] = None) -> str:
        """构建 system prompt: baseline 无 skill, with_skill 注入 skill 内容。"""
        base_prompt = (
            "你是一个有帮助的 AI 助手。"
            "请根据用户的问题给出准确、简洁的回答。"
        )

        if skill_name and skill_name in self.loader.skills:
            skill = self.loader.skills[skill_name]
            skill_body = skill["body"]
            skill_prompt = (
                f"\n\n=== 已加载技能: {skill_name} ===\n"
                f"{skill_body}\n"
                f"=== 技能结束 ===\n"
                f"请在回答时参考以上技能知识。"
            )
            return base_prompt + skill_prompt

        return base_prompt

    def execute(
        self, prompt: str, skill_name: Optional[str] = None
    ) -> Tuple[str, int, float]:
        """执行一次 agent 调用, 返回 (output, total_tokens, duration_seconds)。"""
        system_prompt = self._build_system_prompt(skill_name)

        start_time = time.time()

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )

            duration = time.time() - start_time
            output = response.choices[0].message.content or ""
            total_tokens = response.usage.total_tokens if response.usage else len(output) * 4

            return output, total_tokens, duration

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"[API调用失败] {type(e).__name__}: {e}"
            return error_msg, 0, duration


def create_default_executor(skills_dir: Path) -> RealAgentExecutor:
    """使用 user profile 中的 Agnes AI 配置创建执行器。"""
    return RealAgentExecutor(
        api_key=os.environ.get(
            "AGNES_API_KEY",
            "",
        ),
        base_url=os.environ.get("AGNES_BASE_URL", "https://apihub.agnes-ai.com/v1"),
        model=os.environ.get("AGNES_MODEL", "agnes-1.5-flash"),
        skills_dir=skills_dir,
    )