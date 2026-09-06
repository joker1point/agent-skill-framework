from __future__ import annotations
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Protocol
from datetime import datetime


class Assertion(Protocol):
    def check(self, output: str) -> bool:
        ...

    def get_evidence(self, output: str) -> str:
        ...

    def get_name(self) -> str:
        ...


@dataclass
class EvalResult:
    passed: bool
    evidence: str
    assertion_name: str


@dataclass
class EvalCase:
    id: int
    name: str
    prompt: str
    expected_output: str
    files: List[str] = field(default_factory=list)
    assertions: List[Assertion] = field(default_factory=list)


@dataclass
class RegexAssertion:
    name: str
    pattern: str
    flags: int = re.IGNORECASE

    def check(self, output: str) -> bool:
        return bool(re.search(self.pattern, output, self.flags))

    def get_evidence(self, output: str) -> str:
        match = re.search(self.pattern, output, self.flags)
        if match:
            return f"Found match: '{match.group(0)}'"
        return f"No match found for pattern: {self.pattern}"

    def get_name(self) -> str:
        return self.name


@dataclass
class ContainsAssertion:
    name: str
    substring: str
    case_sensitive: bool = False

    def check(self, output: str) -> bool:
        if self.case_sensitive:
            return self.substring in output
        return self.substring.lower() in output.lower()

    def get_evidence(self, output: str) -> str:
        if self.check(output):
            return f"Found substring: '{self.substring}'"
        return f"Substring '{self.substring}' not found in output"

    def get_name(self) -> str:
        return self.name


@dataclass
class ContainsAllAssertion:
    name: str
    substrings: List[str]
    case_sensitive: bool = False

    def check(self, output: str) -> bool:
        if self.case_sensitive:
            return all(s in output for s in self.substrings)
        return all(s.lower() in output.lower() for s in self.substrings)

    def get_evidence(self, output: str) -> str:
        missing = []
        present = []
        for s in self.substrings:
            if self.case_sensitive:
                if s in output:
                    present.append(s)
                else:
                    missing.append(s)
            else:
                if s.lower() in output.lower():
                    present.append(s)
                else:
                    missing.append(s)
        if missing:
            return f"Missing substrings: {', '.join(missing)}"
        return f"All substrings found: {', '.join(present)}"

    def get_name(self) -> str:
        return self.name


@dataclass
class NotContainsAssertion:
    name: str
    substring: str

    def check(self, output: str) -> bool:
        return self.substring not in output

    def get_evidence(self, output: str) -> str:
        if self.substring in output:
            return f"Found unwanted substring: '{self.substring}'"
        return f"Substring '{self.substring}' correctly absent"

    def get_name(self) -> str:
        return self.name


@dataclass
class LengthAssertion:
    name: str
    min_length: Optional[int] = None
    max_length: Optional[int] = None

    def check(self, output: str) -> bool:
        length = len(output)
        if self.min_length is not None and length < self.min_length:
            return False
        if self.max_length is not None and length > self.max_length:
            return False
        return True

    def get_evidence(self, output: str) -> str:
        length = len(output)
        conditions = []
        if self.min_length is not None:
            conditions.append(f"min {self.min_length}")
        if self.max_length is not None:
            conditions.append(f"max {self.max_length}")
        return f"Output length: {length} chars (expected {', '.join(conditions)})"

    def get_name(self) -> str:
        return self.name


class SkillEvals:
    def __init__(self, skills_dir: Path):
        self.skills_dir = skills_dir
        self.evals_cache: Dict[str, List[EvalCase]] = {}

    def load_evals(self, skill_name: str) -> List[EvalCase]:
        if skill_name in self.evals_cache:
            return self.evals_cache[skill_name]

        evals_file = self.skills_dir / skill_name / "evals" / "evals.json"
        if not evals_file.exists():
            return []

        try:
            with open(evals_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            return []

        evals = []
        for eval_data in data.get("evals", []):
            assertions = self._parse_assertions(eval_data.get("assertions", []))
            evals.append(EvalCase(
                id=eval_data.get("id", 0),
                name=eval_data.get("name", f"eval-{eval_data.get('id', 0)}"),
                prompt=eval_data.get("prompt", ""),
                expected_output=eval_data.get("expected_output", ""),
                files=eval_data.get("files", []),
                assertions=assertions
            ))

        self.evals_cache[skill_name] = evals
        return evals

    def _parse_assertions(self, assertions_data: List[Dict]) -> List[Assertion]:
        assertions = []
        for assert_data in assertions_data:
            assert_type = assert_data.get("type", "contains")
            name = assert_data.get("name", assert_type)

            if assert_type == "regex":
                assertions.append(RegexAssertion(
                    name=name,
                    pattern=assert_data.get("pattern", ""),
                    flags=re.IGNORECASE if assert_data.get("case_insensitive", True) else 0
                ))
            elif assert_type == "contains":
                assertions.append(ContainsAssertion(
                    name=name,
                    substring=assert_data.get("substring", ""),
                    case_sensitive=assert_data.get("case_sensitive", False)
                ))
            elif assert_type == "contains_all":
                assertions.append(ContainsAllAssertion(
                    name=name,
                    substrings=assert_data.get("substrings", []),
                    case_sensitive=assert_data.get("case_sensitive", False)
                ))
            elif assert_type == "not_contains":
                assertions.append(NotContainsAssertion(
                    name=name,
                    substring=assert_data.get("substring", "")
                ))
            elif assert_type == "length":
                assertions.append(LengthAssertion(
                    name=name,
                    min_length=assert_data.get("min_length"),
                    max_length=assert_data.get("max_length")
                ))

        return assertions

    def evaluate_output(self, eval_case: EvalCase, output: str) -> List[EvalResult]:
        results = []
        if eval_case.assertions:
            for assertion in eval_case.assertions:
                passed = assertion.check(output)
                evidence = assertion.get_evidence(output)
                results.append(EvalResult(
                    passed=passed,
                    evidence=evidence,
                    assertion_name=assertion.get_name()
                ))
        else:
            passed = eval_case.expected_output.lower() in output.lower()
            evidence = f"Expected: '{eval_case.expected_output}', Got: '{output[:100]}...'" if len(output) > 100 else f"Expected: '{eval_case.expected_output}', Got: '{output}'"
            results.append(EvalResult(
                passed=passed,
                evidence=evidence,
                assertion_name="expected_output_match"
            ))
        return results

    def create_eval_file(self, skill_name: str, evals: List[Dict]) -> bool:
        evals_dir = self.skills_dir / skill_name / "evals"
        evals_dir.mkdir(parents=True, exist_ok=True)

        data = {
            "skill_name": skill_name,
            "created_at": datetime.now().isoformat(),
            "evals": evals
        }

        try:
            with open(evals_dir / "evals.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except OSError:
            return False

    def list_skills_with_evals(self) -> List[str]:
        skills_with_evals = []
        for skill_dir in self.skills_dir.iterdir():
            if skill_dir.is_dir() and (skill_dir / "evals" / "evals.json").exists():
                skills_with_evals.append(skill_dir.name)
        return skills_with_evals

    def get_eval_summary(self, skill_name: str) -> Dict[str, Any]:
        evals = self.load_evals(skill_name)
        return {
            "skill_name": skill_name,
            "total_evals": len(evals),
            "eval_names": [e.name for e in evals],
            "assertion_count": sum(len(e.assertions) for e in evals)
        }