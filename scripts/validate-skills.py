"""Validate the reusable skill library without executing bundled API or workflow scripts."""
from pathlib import Path
import ast
import re
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {"name", "description", "metadata", "license", "allowed-tools"}

def main():
    errors = []
    skills = sorted((ROOT / "skills").glob("*/SKILL.md"))
    for entry in skills:
        text = entry.read_text(encoding="utf-8")
        try:
            parts = text.split("---", 2)
            if not text.startswith("---\n") or len(parts) != 3:
                raise ValueError("missing YAML frontmatter")
            header = yaml.safe_load(parts[1])
            if header.get("name") != entry.parent.name:
                raise ValueError("name does not match folder")
            if not isinstance(header.get("description"), str) or not header["description"].strip():
                raise ValueError("missing description")
            if set(header) - ALLOWED:
                raise ValueError("unsupported frontmatter keys")
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", header["name"]):
                raise ValueError("invalid skill name")
        except (ValueError, TypeError, AttributeError, yaml.YAMLError) as error:
            errors.append(f"{entry.relative_to(ROOT)}: {error}")
    for path in (ROOT / "skills").rglob("*"):
        if not path.is_file():
            continue
        if path.suffix == ".py":
            try:
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            except (SyntaxError, UnicodeError) as error:
                errors.append(f"{path.relative_to(ROOT)}: {error}")
        if path.suffix in {".yaml", ".yml", ".md"}:
            if path.suffix != ".md":
                try:
                    yaml.safe_load(path.read_text(encoding="utf-8"))
                except yaml.YAMLError as error:
                    errors.append(f"{path.relative_to(ROOT)}: {error}")
            else:
                for target in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
                    target = target.split("#", 1)[0]
                    if not target or ":" in target or target.startswith("/"):
                        continue
                    if not (path.parent / target).exists():
                        errors.append(f"{path.relative_to(ROOT)}: missing {target}")
        if path.name == "SKILL.md" and path.parent.parent != ROOT / "skills":
            errors.append(f"{path.relative_to(ROOT)}: nested skill")
        if path.suffix in {".pyc", ".zip"} or "__pycache__" in path.parts:
            errors.append(f"{path.relative_to(ROOT)}: generated artifact")
    if not skills:
        errors.append("No skills found")
    for error in errors:
        print(error)
    print(f"Validated {len(skills)} skills; {len(errors)} errors")
    return bool(errors)

if __name__ == "__main__":
    sys.exit(main())
