from __future__ import annotations
import os
import shutil
import subprocess
from pathlib import Path


class SkillLinker:
    def __init__(
        self,
        skills_repo: Path | str,
        project_root: Path | str,
        project_skills_dir: str = ".agents/skills",
        agent_skills_dir: str = ".claude/skills",
    ):
        self.skills_repo = Path(skills_repo).resolve()
        self.project_root = Path(project_root).resolve()
        self.project_skills_dir = self.project_root / project_skills_dir
        self.agent_skills_dir = self.project_root / agent_skills_dir

    def _ensure_dir(self, path: Path) -> None:
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)

    def _is_symlink(self, path: Path) -> bool:
        if not path.exists():
            return False
        return path.is_symlink()

    def _create_symlink(self, source: Path, target: Path) -> tuple[bool, str]:
        try:
            if os.name == "nt":
                cmd = f'mklink /D "{target}" "{source}"'
                result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
            else:
                os.symlink(source, target)
            return True, f"✓ 已创建软链接: {target} -> {source}"
        except subprocess.CalledProcessError as e:
            if "拒绝访问" in e.stderr or "privilege" in e.stderr.lower():
                return False, "permission_denied"
            return False, f"创建软链接失败 - {e.stderr}"
        except Exception as e:
            return False, f"创建软链接失败 - {e}"

    def link_skill(self, skill_name: str, source_path: Path | str | None = None, force: bool = False) -> str:
        self._ensure_dir(self.project_skills_dir)

        if source_path is None:
            source_path = self.skills_repo / "skills" / skill_name
        else:
            source_path = Path(source_path).resolve()

        if not source_path.exists():
            return f"Error: 源路径不存在 - {source_path}"

        target_path = self.project_skills_dir / skill_name

        if target_path.exists():
            if self._is_symlink(target_path):
                current_target = str(target_path.resolve())
                if current_target == str(source_path):
                    return f"已存在相同链接: {target_path} -> {source_path}"
                os.remove(target_path)
            elif force:
                shutil.rmtree(target_path)
            else:
                return f"Error: {target_path} 已存在且不是软链接。使用 force=True 强制覆盖。"

        success, msg = self._create_symlink(source_path, target_path)
        if success:
            return msg

        if msg == "permission_denied":
            shutil.copytree(source_path, target_path)
            return f"⚠ 权限不足，已复制文件代替软链接: {target_path}\n   提示：若要使用软链接，请以管理员身份运行终端并执行:\n   mklink /D \"{target_path}\" \"{source_path}\""

        try:
            shutil.copytree(source_path, target_path)
            return f"⚠ 创建软链接失败，已复制文件代替: {target_path}"
        except Exception as e:
            return f"Error: 创建软链接和复制文件均失败 - {e}"

    def unlink_skill(self, skill_name: str) -> str:
        target_path = self.project_skills_dir / skill_name

        if not target_path.exists():
            return f"Error: 不存在该链接 - {target_path}"

        try:
            if target_path.is_symlink() or target_path.is_file():
                os.remove(target_path)
            else:
                shutil.rmtree(target_path)
            return f"✓ 已删除: {target_path}"
        except Exception as e:
            return f"Error: 删除失败 - {e}"

    def update_skill(self, skill_name: str) -> str:
        target_path = self.project_skills_dir / skill_name
        if not target_path.exists():
            return f"Error: 不存在该技能 - {target_path}"

        if self._is_symlink(target_path):
            return "✓ 软链接无需更新，源文件变更会自动同步"

        source_path = self.skills_repo / "skills" / skill_name
        if not source_path.exists():
            return f"Error: 源路径不存在 - {source_path}"

        try:
            shutil.rmtree(target_path)
            shutil.copytree(source_path, target_path)
            return f"✓ 已更新技能: {target_path}"
        except Exception as e:
            return f"Error: 更新失败 - {e}"

    def list_links(self) -> list[dict]:
        links = []
        if not self.project_skills_dir.exists():
            return links

        for item in sorted(self.project_skills_dir.iterdir()):
            if item.is_symlink():
                links.append({
                    "name": item.name,
                    "type": "symlink",
                    "link_path": str(item),
                    "target_path": str(item.resolve()),
                    "exists": item.resolve().exists(),
                })
            elif item.is_dir():
                links.append({
                    "name": item.name,
                    "type": "copied",
                    "link_path": str(item),
                    "target_path": "(复制的目录)",
                    "exists": True,
                })
        return links

    def setup_agent_entry(self) -> str:
        self._ensure_dir(self.project_skills_dir)
        self._ensure_dir(self.agent_skills_dir.parent)

        if self.agent_skills_dir.exists():
            if self._is_symlink(self.agent_skills_dir):
                current_target = str(self.agent_skills_dir.resolve())
                expected_target = str(self.project_skills_dir)
                if current_target == expected_target:
                    return f"✓ Agent入口已存在: {self.agent_skills_dir} -> {self.project_skills_dir}"
                os.remove(self.agent_skills_dir)
            elif os.path.isdir(self.agent_skills_dir):
                shutil.rmtree(self.agent_skills_dir)
            else:
                os.remove(self.agent_skills_dir)

        success, msg = self._create_symlink(self.project_skills_dir, self.agent_skills_dir)
        if success:
            return msg

        if msg == "permission_denied":
            shutil.copytree(self.project_skills_dir, self.agent_skills_dir, dirs_exist_ok=True)
            return f"⚠ 权限不足，已复制文件代替软链接: {self.agent_skills_dir}\n   提示：若要使用软链接，请以管理员身份运行终端并执行:\n   mklink /D \"{self.agent_skills_dir}\" \"{self.project_skills_dir}\""

        try:
            shutil.copytree(self.project_skills_dir, self.agent_skills_dir, dirs_exist_ok=True)
            return f"⚠ 创建软链接失败，已复制文件代替: {self.agent_skills_dir}"
        except Exception as e:
            return f"Error: 创建Agent入口和复制文件均失败 - {e}"

    def link_from_repo(self, skill_name: str, repo_name: str) -> str:
        source_path = self.skills_repo / repo_name / "skills" / skill_name
        return self.link_skill(skill_name, source_path)

    def create_skill(self, skill_name: str, description: str = "", tags: str = "") -> str:
        skill_dir = self.project_skills_dir / skill_name
        if skill_dir.exists():
            return f"Error: Skill已存在 - {skill_dir}"

        try:
            skill_dir.mkdir(parents=True, exist_ok=True)
            skill_file = skill_dir / "SKILL.md"
            content = f"""---
name: {skill_name}
description: {description}
tags: {tags}
always: false
---

# {skill_name}

技能内容...
"""
            skill_file.write_text(content, encoding="utf-8")
            return f"✓ 已创建新Skill: {skill_file}"
        except Exception as e:
            return f"Error: 创建Skill失败 - {e}"

    def sync_all(self) -> str:
        results = []
        for link in self.list_links():
            if link["type"] == "copied":
                result = self.update_skill(link["name"])
                results.append(result)
        if results:
            return "\n".join(results)
        return "✓ 所有技能已是最新状态"

    def install_all(self, skill_names: list[str]) -> str:
        results = []
        for name in skill_names:
            result = self.link_skill(name)
            results.append(result)
        return "\n".join(results)