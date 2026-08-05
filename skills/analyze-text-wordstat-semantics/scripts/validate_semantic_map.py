#!/usr/bin/env python3
"""Validate an analyze-text-wordstat-semantics JSON result."""

import json
import csv
import re
import sys
from pathlib import Path

EVIDENCE = {"MEASURED", "USER_PROVIDED", "ESTIMATED", "UNKNOWN"}
STATUSES = {"PASS", "NEEDS_INPUT", "NO_ELIGIBLE_KEYWORD"}
REQUIRED_KEY_FIELDS = {
    "phrase", "checked_query", "frequency_type", "frequency", "region", "device", "tab",
    "period", "checked_at", "evidence_status", "source", "evidence_locator",
    "evidence_kind", "intent_fit", "coverage_evidence", "match_type", "selection_constraint"
}
CATEGORY_NAMES = {
    1: "Основная тема и сущность", 2: "Синонимы и варианты названия", 3: "Виды и подкатегории",
    4: "Компоненты и состав", 5: "Материалы и технологии", 6: "Свойства и характеристики",
    7: "Процессы и этапы", 8: "Сценарии применения", 9: "Проблемы и боли",
    10: "Польза и результаты", 11: "Критерии выбора", 12: "Сравнения и различия",
    13: "Альтернативы и заменители", 14: "Аудитория и роли", 15: "Коммерческие модификаторы",
    16: "География и локальность", 17: "Информационные вопросы", 18: "Доверие и доказательства",
    19: "Ограничения и риски", 20: "Связанные сущности", 21: "Действия и следующий шаг"
}
INTENTS = {"informational", "commercial_investigation", "transactional", "navigational", "local"}


def norm(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower().replace("ё", "е"))


def validate_candidate(candidate: object, label: str, errors: list[str], reference: dict | None = None) -> None:
    if not isinstance(candidate, dict):
        errors.append(f"{label} must be an object")
        return
    required = REQUIRED_KEY_FIELDS | ({"reason"} if label.startswith("rejected_candidates") else set())
    missing = sorted(required - candidate.keys())
    if missing:
        errors.append(f"{label} missing: " + ", ".join(missing))
        return
    for field in required - {"frequency"}:
        if not isinstance(candidate[field], str) or not candidate[field].strip():
            errors.append(f"{label}.{field} must be a non-empty string")
    frequency = candidate.get("frequency")
    if not isinstance(frequency, int) or isinstance(frequency, bool) or frequency < 0:
        errors.append(f"{label}.frequency must be a non-negative integer")
    if candidate.get("evidence_status") not in {"MEASURED", "USER_PROVIDED"}:
        errors.append(f"{label}.evidence_status must be MEASURED or USER_PROVIDED")
    if candidate.get("frequency_type") != "top_query":
        errors.append(f"{label}.frequency_type must be top_query")
    if candidate.get("tab") != "Топы запросов" or candidate.get("period") != "последний месяц":
        errors.append(f"{label} must use tab 'Топы запросов' and period 'последний месяц'")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(candidate.get("checked_at", ""))):
        errors.append(f"{label}.checked_at must use YYYY-MM-DD")
    if not str(candidate.get("phrase", "")).strip() or not str(candidate.get("checked_query", "")).strip():
        errors.append(f"{label}.phrase and checked_query must be non-empty")
    if candidate.get("intent_fit") not in {"high", "medium", "low"}:
        errors.append(f"{label}.intent_fit must be high, medium, or low")
    if candidate.get("match_type") not in {"exact_intent", "broad_parent", "partial", "other_intent"}:
        errors.append(f"{label}.match_type is invalid")
    evidence_kind = candidate.get("evidence_kind")
    if evidence_kind not in {"csv", "screenshot", "api", "url"}:
        errors.append(f"{label}.evidence_kind is invalid")
    if evidence_kind == "csv":
        row_number = candidate.get("evidence_row")
        evidence_file = candidate.get("evidence_file")
        if not isinstance(row_number, int) or isinstance(row_number, bool) or row_number < 2:
            errors.append(f"{label}.evidence_row must be an integer >= 2")
            return
        if not isinstance(evidence_file, str) or not evidence_file.strip():
            errors.append(f"{label}.evidence_file is required for csv")
            return
        path = Path(evidence_file)
        if not path.is_file():
            errors.append(f"{label}.evidence_file does not exist: {evidence_file}")
        else:
            try:
                rows = list(csv.reader(path.read_text(encoding="utf-8-sig").splitlines(), delimiter=";"))
                row = rows[row_number - 1]
                if len(row) < 2 or norm(row[0]) != norm(str(candidate.get("phrase", ""))):
                    errors.append(f"{label} phrase does not match CSV row {row_number}")
                elif int(row[1]) != frequency:
                    errors.append(f"{label} frequency does not match CSV row {row_number}")
                header = rows[0][2] if rows and len(rows[0]) > 2 else ""
                for value, field in ((candidate.get("checked_query"), "checked_query"), (candidate.get("region"), "region"), (candidate.get("device"), "device")):
                    if norm(str(value)) not in norm(header):
                        errors.append(f"{label}.{field} does not match CSV header")
            except (OSError, ValueError, IndexError) as exc:
                errors.append(f"{label} cannot verify CSV evidence: {exc}")
    if reference:
        for field in ("region", "device", "tab", "period", "frequency_type", "checked_at"):
            if candidate.get(field) != reference.get(field):
                errors.append(f"{label}.{field} must match main_keyword")


def validate(data: dict) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    status = data.get("status")
    if status not in STATUSES:
        errors.append("status must be PASS, NEEDS_INPUT, or NO_ELIGIBLE_KEYWORD")

    intent = data.get("intent", {})
    if intent.get("primary") not in INTENTS or not intent.get("summary"):
        errors.append("intent.primary and intent.summary are required")
    if len(intent.get("evidence", [])) < 2:
        errors.append("intent must have at least two evidence items")

    keyword = data.get("main_keyword")
    categories = data.get("categories")
    if status == "NEEDS_INPUT":
        if keyword is not None:
            errors.append("main_keyword must be null for NEEDS_INPUT")
        if categories != []:
            errors.append("categories must be empty for NEEDS_INPUT")
    if status == "NO_ELIGIBLE_KEYWORD" and categories != []:
        errors.append("categories must be empty for NO_ELIGIBLE_KEYWORD")
    if status == "PASS":
        if not isinstance(keyword, dict):
            errors.append("main_keyword is required for PASS")
        else:
            validate_candidate(keyword, "main_keyword", errors)
            if keyword.get("match_type") == "exact_intent" and keyword.get("intent_fit") != "high":
                errors.append("exact_intent main keyword must have high intent_fit")
            if keyword.get("match_type") == "broad_parent" and keyword.get("intent_fit") not in {"high", "medium"}:
                errors.append("broad_parent main keyword must have high or medium intent_fit")
            frequency = keyword.get("frequency")
            if not isinstance(frequency, int) or isinstance(frequency, bool) or not 1000 <= frequency <= 5000:
                errors.append("main_keyword.frequency must be an integer from 1000 to 5000")
        rejected = data.get("rejected_candidates", [])
        if not isinstance(rejected, list) or len(rejected) < 2:
            errors.append("PASS requires at least two rejected_candidates")
        else:
            for index, candidate in enumerate(rejected):
                validate_candidate(candidate, f"rejected_candidates[{index}]", errors, keyword)

    if status == "NO_ELIGIBLE_KEYWORD":
        rejected = data.get("rejected_candidates", [])
        if not isinstance(rejected, list) or len(rejected) < 3:
            errors.append("NO_ELIGIBLE_KEYWORD requires at least three verified candidates")
        else:
            for index, candidate in enumerate(rejected):
                validate_candidate(candidate, f"rejected_candidates[{index}]", errors)
                frequency = candidate.get("frequency") if isinstance(candidate, dict) else None

    if not isinstance(categories, list):
        errors.append("categories must be a list")
        categories = []
    ids = [item.get("id") for item in categories if isinstance(item, dict)]
    if status == "PASS" and sorted(ids) != list(range(1, 22)):
        errors.append("categories must contain each id from 1 to 21 exactly once")

    seen: set[str] = set()
    group_count = 0
    for item in categories:
        if not isinstance(item, dict):
            errors.append("each category must be an object")
            continue
        if item.get("name") != CATEGORY_NAMES.get(item.get("id")):
            errors.append(f"category {item.get('id')} has an incorrect name")
        groups = item.get("groups", [])
        na_reason = item.get("na_reason")
        if not groups and not (isinstance(na_reason, str) and na_reason.strip()):
            errors.append(f"category {item.get('id')} needs groups or na_reason")
        for group in groups:
            group_count += 1
            canonical = group.get("canonical", "")
            if not isinstance(canonical, str) or not canonical.strip():
                errors.append(f"category {item.get('id')} has an empty canonical term")
                continue
            key = norm(canonical)
            if key in seen:
                errors.append(f"duplicate canonical term: {canonical}")
            seen.add(key)
            if not group.get("source"):
                errors.append(f"term '{canonical}' has no source")
            if not group.get("evidence_locator"):
                errors.append(f"term '{canonical}' has no evidence_locator")
            if not group.get("relation_evidence"):
                errors.append(f"term '{canonical}' has no relation_evidence")
            if group.get("relevance_status") != "INCLUDED":
                errors.append(f"term '{canonical}' must have relevance_status INCLUDED")
            if group.get("evidence_status") not in EVIDENCE:
                errors.append(f"term '{canonical}' has invalid evidence_status")
    if status == "PASS" and group_count == 0:
        errors.append("PASS requires at least one semantic group")
    if status == "PASS":
        checks = data.get("checks")
        required_checks = {
            "single_intent_and_keyword", "frequency_in_range", "frequency_evidenced",
            "measurement_parameters_complete", "all_categories_accounted", "noise_removed",
            "groups_relevant", "group_evidence_complete"
        }
        if not isinstance(checks, dict) or set(checks) != required_checks or not all(value is True for value in checks.values()):
            errors.append("PASS requires exactly eight successful checks")
        handoff = data.get("handoff_summary")
        if not isinstance(handoff, dict) or set(handoff) != {"confirmed", "estimated", "unknown", "next_data"}:
            errors.append("PASS requires complete handoff_summary")
        elif not all(isinstance(handoff[key], list) for key in handoff):
            errors.append("handoff_summary values must be lists")
    return errors, warnings


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: validate_semantic_map.py RESULT.json", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    errors, warnings = validate(data)
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAIL: {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    print(f"PASS: 0 errors, {len(warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
