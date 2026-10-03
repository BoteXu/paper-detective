#!/usr/bin/env python3
"""Check distribution invariants without installing an extra validator package."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "paper-detective"


def main():
    problems = []
    required = ["SKILL.md", "agents/openai.yaml", "assets/report-template.md", "references/retrieval.md", "references/report-format.md", "scripts/validate_report.py", "LICENSE"]
    for relative in required:
        if not (SKILL / relative).is_file():
            problems.append(f"Missing distribution file: {relative}")
    if not (SKILL / "SKILL.md").is_file():
        print("\n".join(problems))
        return 1
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    if not match:
        problems.append("Missing YAML frontmatter block")
    else:
        fields = dict(re.findall(r"^([a-z_-]+):\s*(.+)$", match.group(1), re.M))
        if fields.get("name") != "paper-detective" or not fields.get("description", "").strip():
            problems.append("Missing name or useful description")
    if "[TODO:" in text:
        problems.append("Unfinished skill scaffold")
    for relative in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
        if "://" not in relative and not (SKILL / relative).is_file():
            problems.append(f"Broken skill reference: {relative}")
    if (SKILL / "agents/openai.yaml").is_file():
        metadata = (SKILL / "agents/openai.yaml").read_text(encoding="utf-8")
        if "$paper-detective" not in metadata:
            problems.append("Default prompt must invoke the skill by name")
    for path in SKILL.rglob("*"):
        if path.is_file() and path.suffix in {".md", ".py", ".yaml"}:
            content = path.read_text(encoding="utf-8")
            if re.search(r"[A-Za-z]:[\\/]GPT[\\/]|C:[\\/]Users[\\/]", content):
                problems.append(f"Machine-specific private path in distribution: {path.relative_to(SKILL)}")
    if problems:
        print("\n".join(problems))
        return 1
    print("Skill package checks passed; this does not validate scientific behavior.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
