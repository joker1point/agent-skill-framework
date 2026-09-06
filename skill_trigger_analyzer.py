from __future__ import annotations
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from skills_loader import SkillsLoader


@dataclass
class TriggerAnalysis:
    skill_name: str
    description: str
    trigger_keywords: List[str]
    sample_prompts: List[str]
    false_positives: List[str]
    false_negatives: List[str]
    suggestions: List[str]
    quality_score: float


@dataclass
class TriggerKeyword:
    keyword: str
    score: float
    occurrences: int
    context: List[str]


class SkillTriggerAnalyzer:
    def __init__(self, skills_dir: Path):
        self.skills_dir = skills_dir
        self.loader = SkillsLoader(skills_dir)

    def analyze_trigger(self, skill_name: str, sample_prompts: List[str]) -> TriggerAnalysis:
        skill = self.loader.skills.get(skill_name)
        if not skill:
            raise ValueError(f"Skill not found: {skill_name}")

        description = skill["meta"].get("description", "")

        keywords = self._extract_keywords(description)
        false_positives = []
        false_negatives = []

        for prompt in sample_prompts:
            should_trigger = self._should_trigger(keywords, prompt)
            is_related = self._is_prompt_related(keywords, prompt)

            if should_trigger and not is_related:
                false_positives.append(prompt)
            elif is_related and not should_trigger:
                false_negatives.append(prompt)

        suggestions = self._generate_suggestions(description, keywords, false_positives, false_negatives)
        quality_score = self._calculate_quality_score(false_positives, false_negatives, keywords)

        return TriggerAnalysis(
            skill_name=skill_name,
            description=description,
            trigger_keywords=keywords,
            sample_prompts=sample_prompts,
            false_positives=false_positives,
            false_negatives=false_negatives,
            suggestions=suggestions,
            quality_score=quality_score
        )

    def _extract_keywords(self, description: str) -> List[str]:
        words = re.findall(r'\b[a-zA-Z]{3,}\b', description.lower())
        stop_words = {"the", "and", "for", "with", "when", "use", "this", "that", "from", "to", "of", "in", "on", "at", "by", "as", "an", "or", "is", "are", "be", "been", "being", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should", "may", "might", "must", "shall", "can", "need", "dare", "ought", "used", "to", "through", "during", "before", "after", "between", "under", "above", "below", "about", "against", "among", "into", "onto", "upon", "within", "without", "throughout", "since", "until", "till", "towards", "toward", "beyond", "despite", "in", "out", "up", "down", "off", "over", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "just", "even", "still", "also", "enough", "almost", "quite", "rather", "very", "much", "many", "little", "less", "least", "both", "few", "several", "either", "neither", "each", "every", "all", "any", "another", "other", "such", "what", "which", "who", "whom", "whose", "this", "that", "these", "those", "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them", "my", "your", "his", "its", "our", "their", "mine", "yours", "his", "hers", "ours", "theirs"}
        unique_words = [w for w in words if w not in stop_words]
        return list(set(unique_words))

    def _should_trigger(self, keywords: List[str], prompt: str) -> bool:
        prompt_lower = prompt.lower()
        keyword_matches = sum(1 for kw in keywords if kw in prompt_lower)
        return keyword_matches >= 1

    def _is_prompt_related(self, keywords: List[str], prompt: str) -> bool:
        prompt_lower = prompt.lower()
        keyword_matches = sum(1 for kw in keywords if kw in prompt_lower)
        keyword_density = keyword_matches / max(len(keywords), 1)
        return keyword_density >= 0.3

    def _generate_suggestions(
        self,
        description: str,
        keywords: List[str],
        false_positives: List[str],
        false_negatives: List[str]
    ) -> List[str]:
        suggestions = []

        if false_positives:
            suggestions.append("Reduce false positives by adding more specific context to the description.")

        if false_negatives:
            suggestions.append("Increase triggering by expanding keyword coverage or making the description more 'pushy'.")

        if len(keywords) < 5:
            suggestions.append(f"Add more specific keywords to improve triggering accuracy.")

        if len(keywords) > 20:
            suggestions.append("Consider reducing overly broad keywords that may cause false triggers.")

        if not description.endswith("."):
            suggestions.append("End the description with a period for proper formatting.")

        if len(description) < 50:
            suggestions.append("Expand the description to include more specific trigger contexts.")

        if len(description) > 500:
            suggestions.append("Consider shortening the description while keeping key trigger phrases.")

        return suggestions

    def _calculate_quality_score(self, false_positives: List[str], false_negatives: List[str], keywords: List[str]) -> float:
        total = len(false_positives) + len(false_negatives)
        if total == 0:
            score = 100.0
        else:
            score = max(0, 100 - (len(false_positives) * 10 + len(false_negatives) * 15))

        keyword_bonus = min(len(keywords) * 2, 20)
        score = min(100, score + keyword_bonus)

        return round(score, 2)

    def optimize_description(self, skill_name: str, sample_prompts: List[str]) -> Dict[str, Any]:
        analysis = self.analyze_trigger(skill_name, sample_prompts)
        skill = self.loader.skills.get(skill_name)
        if not skill:
            return {"error": "Skill not found"}

        current_description = analysis.description
        optimized_description = current_description

        if analysis.false_negatives:
            missed_keywords = set()
            for prompt in analysis.false_negatives:
                words = re.findall(r'\b[a-zA-Z]{3,}\b', prompt.lower())
                missed_keywords.update(words)

            missed_keywords -= set(analysis.trigger_keywords)
            if missed_keywords:
                additional_context = f" Make sure to use this skill whenever the user mentions: {', '.join(list(missed_keywords)[:5])}."
                if additional_context not in optimized_description:
                    optimized_description += additional_context

        if analysis.false_positives:
            for prompt in analysis.false_positives[:3]:
                words = re.findall(r'\b[a-zA-Z]{3,}\b', prompt.lower())
                problematic_words = set(words) & set(analysis.trigger_keywords)
                if problematic_words:
                    optimized_description += f" Do NOT use this skill for: {', '.join(list(problematic_words)[:3])}."

        return {
            "skill_name": skill_name,
            "original_description": current_description,
            "optimized_description": optimized_description,
            "analysis": {
                "quality_score": analysis.quality_score,
                "false_positives": len(analysis.false_positives),
                "false_negatives": len(analysis.false_negatives),
                "suggestions": analysis.suggestions
            }
        }

    def batch_analyze(self, sample_prompts: List[str]) -> List[TriggerAnalysis]:
        results = []
        for skill_name in self.loader.list_skills():
            try:
                analysis = self.analyze_trigger(skill_name, sample_prompts)
                results.append(analysis)
            except ValueError:
                continue
        return sorted(results, key=lambda x: x.quality_score, reverse=True)