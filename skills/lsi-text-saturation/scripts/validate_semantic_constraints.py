#!/usr/bin/env python3
"""Validate exact phrases and custom word-form groups in edited text."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


WORD = re.compile(r"[0-9a-zа-я]+(?:-[0-9a-zа-я]+)*", re.IGNORECASE)


def normalize(value: object) -> str:
    return " ".join(WORD.findall(str(value or "").lower().replace("ё", "е")))


def count_phrase(text_tokens: list[str], phrase: str) -> int:
    wanted = normalize(phrase).split()
    if not wanted:
        return 0
    size = len(wanted)
    return sum(text_tokens[index:index + size] == wanted for index in range(len(text_tokens) - size + 1))


def count_group(text_tokens: list[str], forms: list[str]) -> int:
    wanted = {normalize(form) for form in forms}
    wanted.discard("")
    return sum(token in wanted for token in text_tokens)


def audit_item(label: str, actual: int, minimum: int, maximum: int | None) -> dict[str, object]:
    passed = actual >= minimum and (maximum is None or actual <= maximum)
    return {
        "label": label,
        "actual": actual,
        "minimum": minimum,
        "maximum": maximum,
        "passed": passed,
    }


def bounds(rule: dict[str, object], label: str) -> tuple[int, int | None]:
    minimum = int(rule.get("min", 0))
    raw_maximum = rule.get("max")
    maximum = None if raw_maximum is None else int(raw_maximum)
    if minimum < 0 or (maximum is not None and maximum < 0):
        raise SystemExit(f"Отрицательная граница в правиле: {label}")
    if maximum is not None and minimum > maximum:
        raise SystemExit(f"Минимум выше максимума в правиле: {label}")
    return minimum, maximum


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", type=Path, required=True)
    parser.add_argument("--rules", type=Path, required=True)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    text_tokens = normalize(args.text.read_text(encoding="utf-8-sig")).split()
    rules = json.loads(args.rules.read_text(encoding="utf-8-sig"))
    if not isinstance(rules, dict):
        raise SystemExit("Файл правил должен содержать JSON-объект")
    if not rules.get("exact_phrases") and not rules.get("groups"):
        raise SystemExit("Файл правил пуст: нет exact_phrases или groups")
    results: list[dict[str, object]] = []
    seen: set[tuple[str, str]] = set()
    seen_group_forms: list[tuple[str, set[str]]] = []

    for rule in rules.get("exact_phrases", []):
        phrase = str(rule["phrase"])
        key = ("exact_phrase", normalize(phrase))
        if not key[1] or key in seen:
            raise SystemExit(f"Пустое или дублирующееся правило точной фразы: {phrase}")
        seen.add(key)
        actual = count_phrase(text_tokens, phrase)
        minimum, maximum = bounds(rule, phrase)
        item = audit_item(phrase, actual, minimum, maximum)
        item["kind"] = "exact_phrase"
        results.append(item)

    for rule in rules.get("groups", []):
        label = str(rule["label"])
        forms = [str(form) for form in rule.get("forms", [label])]
        normalized_forms = [normalize(form) for form in forms]
        if not normalize(label) or not normalized_forms or any(len(form.split()) != 1 for form in normalized_forms):
            raise SystemExit(f"Группа должна содержать непустые однословные словоформы: {label}")
        signature = "|".join(sorted(set(normalized_forms)))
        key = ("wordform_group", signature)
        if key in seen:
            raise SystemExit(f"Дублирующееся правило группы словоформ: {label}")
        form_set = set(normalized_forms)
        overlap = next(((old_label, form_set & old_forms) for old_label, old_forms in seen_group_forms if form_set & old_forms), None)
        if overlap:
            old_label, shared = overlap
            raise SystemExit(
                f"Пересекающиеся группы словоформ: {old_label} / {label}; формы: {', '.join(sorted(shared))}"
            )
        seen.add(key)
        seen_group_forms.append((label, form_set))
        actual = count_group(text_tokens, forms)
        minimum, maximum = bounds(rule, label)
        item = audit_item(label, actual, minimum, maximum)
        item["kind"] = "wordform_group"
        item["forms"] = forms
        results.append(item)

    failed = [item for item in results if not item["passed"]]
    output = {
        "text": str(args.text),
        "rules": str(args.rules),
        "passed": not failed,
        "checked": len(results),
        "failed": len(failed),
        "results": results,
    }
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"CONSTRAINTS={len(results)} FAILED={len(failed)} PASS={int(not failed)}")
    for item in failed:
        print(
            f"FAIL {item['kind']}: {item['label']} actual={item['actual']} "
            f"min={item['minimum']} max={item['maximum']}"
        )
    return 1 if args.strict and failed else 0


if __name__ == "__main__":
    sys.exit(main())
