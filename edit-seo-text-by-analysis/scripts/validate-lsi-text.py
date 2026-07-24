#!/usr/bin/env python3
"""Count analyzer word-form groups in source and edited UTF-8 text files."""

from __future__ import annotations

import argparse
from collections import Counter
import json
import re
import sys
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
NS = {"x": MAIN_NS, "r": REL_NS}
FUNCTION_WORDS = {
    "а",
    "без",
    "в",
    "во",
    "для",
    "до",
    "за",
    "и",
    "из",
    "или",
    "к",
    "как",
    "на",
    "над",
    "но",
    "о",
    "об",
    "от",
    "по",
    "под",
    "при",
    "про",
    "с",
    "со",
    "у",
}


def normalize(value: Any) -> str:
    return str(value or "").casefold().replace("\u0451", "е")


def normalize_header(value: Any) -> str:
    return re.sub(r"\s+", " ", normalize(value)).strip()


def number(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value or "").strip().replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return None


def clean_number(value: float | None) -> int | float | None:
    if value is None:
        return None
    return int(value) if value.is_integer() else value


def relation_key(value: Any) -> str:
    parsed = number(value)
    if parsed is not None:
        return str(clean_number(parsed))
    return normalize_header(value)


def column_number(reference: str) -> int:
    letters = re.match(r"[A-Za-z]+", reference)
    if not letters:
        return 0
    result = 0
    for char in letters.group(0).upper():
        result = result * 26 + ord(char) - ord("A") + 1
    return result - 1


def shared_strings(archive: zipfile.ZipFile) -> list[str]:
    try:
        root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    except KeyError:
        return []
    values = []
    for item in root.findall("x:si", NS):
        values.append("".join(node.text or "" for node in item.findall(".//x:t", NS)))
    return values


def workbook_sheets(archive: zipfile.ZipFile) -> list[tuple[str, str]]:
    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    relations = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    targets = {
        rel.attrib["Id"]: rel.attrib["Target"]
        for rel in relations.findall(f"{{{PKG_REL_NS}}}Relationship")
    }
    result = []
    for sheet in workbook.findall("x:sheets/x:sheet", NS):
        relation_id = sheet.attrib.get(f"{{{REL_NS}}}id")
        target = targets.get(relation_id or "", "")
        if target.startswith("/"):
            target = target.lstrip("/")
        elif not target.startswith("xl/"):
            target = "xl/" + target.lstrip("/")
        result.append((sheet.attrib.get("name", target), target.replace("\\", "/")))
    return result


def cell_value(cell: ET.Element, strings: list[str]) -> Any:
    cell_type = cell.attrib.get("t")
    if cell_type == "inlineStr":
        return "".join(node.text or "" for node in cell.findall(".//x:t", NS))
    value_node = cell.find("x:v", NS)
    if value_node is None:
        return ""
    raw = value_node.text or ""
    if cell_type == "s":
        try:
            return strings[int(raw)]
        except (ValueError, IndexError):
            return raw
    if cell_type in {"str", "e"}:
        return raw
    parsed = number(raw)
    return clean_number(parsed) if parsed is not None else raw


def read_xlsx(path: Path) -> list[dict[str, Any]]:
    with zipfile.ZipFile(path) as archive:
        strings = shared_strings(archive)
        result = []
        for sheet_name, target in workbook_sheets(archive):
            try:
                root = ET.fromstring(archive.read(target))
            except KeyError:
                continue
            rows = []
            for row_node in root.findall(".//x:sheetData/x:row", NS):
                cells: dict[int, Any] = {}
                for cell in row_node.findall("x:c", NS):
                    index = column_number(cell.attrib.get("r", "A1"))
                    cells[index] = cell_value(cell, strings)
                if cells:
                    width = max(cells) + 1
                    rows.append([cells.get(index, "") for index in range(width)])
            result.append({"name": sheet_name, "rows": rows})
        return result


def header_row(sheet: dict[str, Any]) -> tuple[int, list[Any]] | None:
    for index, row in enumerate(sheet["rows"]):
        if any(str(value or "").strip() for value in row):
            return index, row
    return None


def find_column(headers: list[Any], aliases: list[str]) -> int | None:
    normalized = [normalize_header(value) for value in headers]
    normalized_aliases = [normalize_header(alias) for alias in aliases]
    for alias in normalized_aliases:
        for index, header in enumerate(normalized):
            if header == alias or header.startswith(alias + " ("):
                return index
    return None


def value_at(row: list[Any], index: int | None) -> Any:
    if index is None or index >= len(row):
        return ""
    return row[index]


def split_forms(value: Any) -> list[str]:
    return [
        item.strip()
        for item in re.split(r"[,;\r\n]+", str(value or ""))
        if item.strip()
    ]


def read_text_auto(path: Path) -> str:
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "cp1251"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Не удалось определить кодировку файла {path}")


def simple_word_list(path: Path | None) -> list[str]:
    if path is None:
        return []
    result = []
    seen = set()
    for item in re.split(r"[,;\r\n]+", read_text_auto(path)):
        word = item.strip()
        key = normalize_header(word)
        if word and key and key not in seen:
            seen.add(key)
            result.append(word)
    return result


def irrelevant_rows(path: Path | None) -> list[dict[str, Any]]:
    if path is None:
        return []
    text = read_text_auto(path)
    pattern = re.compile(
        r"нерелевантное слово\s*\(точная словоформа\)\s+(.+?)\s+"
        r"у вас повторяется\s+(\d+)\s+раз",
        re.IGNORECASE,
    )
    result = []
    seen = set()
    for match in pattern.finditer(text):
        form = match.group(1).strip()
        key = normalize_header(form)
        if not key or key in seen:
            continue
        seen.add(key)
        result.append(
            {
                "form": form,
                "reported_current": int(match.group(2)),
                "target": 0,
            }
        )
    remaining_lines = []
    for line in text.splitlines():
        normalized_line = normalize_header(line)
        if not normalized_line or normalized_line == "нерелевантные слова":
            continue
        if pattern.search(line):
            continue
        remaining_lines.append(line)
    for form in re.split(r"[,;\r\n]+", "\n".join(remaining_lines)):
        form = form.strip()
        explicit_target = re.match(r"^(.+?)\s*(?:->|=>)\s*(\d+)$", form)
        target = 0
        if explicit_target:
            form = explicit_target.group(1).strip()
            target = int(explicit_target.group(2))
        key = normalize_header(form)
        if form and key and key not in seen:
            seen.add(key)
            result.append(
                {
                    "form": form,
                    "reported_current": None,
                    "target": target,
                }
            )
    return result


def fact_tokens(text: str) -> set[str]:
    return {
        normalize(item).replace(",", ".")
        for item in re.findall(
            r"(?iu)(?:[a-zа-я]*\d+[a-zа-я0-9-]*|\d+(?:[.,]\d+)*|[%₽])",
            text,
        )
    }


def detect_sheet(
    workbook: list[dict[str, Any]],
    required: dict[str, list[str]],
    preferred_name: str | None = None,
) -> tuple[dict[str, Any], int, dict[str, int]] | None:
    matches = []
    for sheet in workbook:
        found = header_row(sheet)
        if not found:
            continue
        row_index, headers = found
        columns = {
            field: find_column(headers, aliases) for field, aliases in required.items()
        }
        if all(index is not None for index in columns.values()):
            score = 1 if preferred_name and preferred_name in normalize(sheet["name"]) else 0
            matches.append((score, sheet, row_index, columns))
    if not matches:
        return None
    _, sheet, row_index, columns = sorted(matches, key=lambda item: item[0], reverse=True)[0]
    return sheet, row_index, {key: int(value) for key, value in columns.items()}


def depth_rows(path: Path | None) -> list[dict[str, Any]]:
    if path is None:
        return []
    workbook = read_xlsx(path)
    detected = detect_sheet(
        workbook,
        {
            "word": ["слово"],
            "forms": ["словоформы", "словоформа"],
        },
        "глубин",
    )
    if detected is None:
        raise ValueError(f"Не найдена таблица глубины в {path}")
    sheet, header_index, columns = detected
    headers = sheet["rows"][header_index]
    repeats_column = find_column(headers, ["повторы", "текст у вас"])
    minimum_column = find_column(headers, ["минимум по рекомендациям"])
    maximum_column = find_column(headers, ["максимум по рекомендациям"])
    delta_column = find_column(headers, ["добавить/удалить"])
    if all(
        item is None
        for item in (
            repeats_column,
            minimum_column,
            maximum_column,
            delta_column,
        )
    ):
        raise ValueError(f"В таблице глубины нет числовых рекомендаций: {path}")
    result = []
    for row in sheet["rows"][header_index + 1 :]:
        word = str(value_at(row, columns["word"]) or "").strip()
        if not word:
            continue
        forms = set(split_forms(value_at(row, columns["forms"])))
        forms.add(word)
        result.append(
            {
                "word": word,
                "forms": sorted(forms, key=normalize),
                "repeats": number(value_at(row, repeats_column)),
                "minimum": number(value_at(row, minimum_column)),
                "maximum": number(value_at(row, maximum_column)),
                "delta": number(value_at(row, delta_column)),
            }
        )
    return result


def lsi_groups(
    path: Path,
    depth: list[dict[str, Any]],
    breadth_limit: int,
) -> list[dict[str, Any]]:
    workbook = read_xlsx(path)
    required = {
        "word": ["слова", "слово"],
        "median": ["медиана"],
        "link": ["связь слов с другим листом"],
    }
    summary = detect_sheet(workbook, required, "сводим форм")
    forms_sheet = detect_sheet(workbook, required, "все форм")
    if summary is None:
        raise ValueError(f"Не найдена LSI-таблица в {path}")
    if forms_sheet is None:
        forms_sheet = summary

    form_sheet, form_header, form_columns = forms_sheet
    forms_by_link: dict[str, set[str]] = {}
    for row in form_sheet["rows"][form_header + 1 :]:
        word = str(value_at(row, form_columns["word"]) or "").strip()
        link = relation_key(value_at(row, form_columns["link"]))
        if word and link:
            forms_by_link.setdefault(link, set()).add(word)

    supplemental = {
        normalize_header(item["word"]): item["forms"] for item in depth if item["word"]
    }
    sheet, header_index, columns = summary
    headers = sheet["rows"][header_index]
    current_column = find_column(
        headers,
        ["текст у вас", "ваша страница", "ваша страница (повторы)"],
    )
    result = []
    seen: set[str] = set()
    for row in sheet["rows"][header_index + 1 :]:
        word = str(value_at(row, columns["word"]) or "").strip()
        word_key = normalize_header(word)
        if not word or word_key in seen:
            continue
        seen.add(word_key)
        if len(result) >= breadth_limit:
            break
        median = number(value_at(row, columns["median"]))
        link = relation_key(value_at(row, columns["link"]))
        forms = set(forms_by_link.get(link, set()))
        forms.add(word)
        forms.update(supplemental.get(word_key, []))
        result.append(
            {
                "breadth_rank": len(result) + 1,
                "word": word,
                "forms": sorted(forms, key=normalize),
                "median": median,
                "analyzer_current": number(value_at(row, current_column)),
            }
        )
    return result


def phrase_rows(path: Path | None) -> list[dict[str, Any]]:
    if path is None:
        return []
    workbook = read_xlsx(path)
    detected = detect_sheet(
        workbook,
        {
            "phrase": ["n-граммы", "n-граммы (включая все словоформы)"],
            "median": ["медианное вхождение"],
        },
        "n-грамм",
    )
    if detected is None:
        raise ValueError(f"Не найдена таблица N-грамм в {path}")
    sheet, header_index, columns = detected
    current_column = find_column(sheet["rows"][header_index], ["на нашем сайте"])
    result = []
    for row in sheet["rows"][header_index + 1 :]:
        phrase = str(value_at(row, columns["phrase"]) or "").strip()
        median = number(value_at(row, columns["median"]))
        if phrase and median is not None:
            result.append(
                {
                    "phrase": phrase,
                    "median": median,
                    "analyzer_current": number(value_at(row, current_column)),
                }
            )
    return result


def count_forms(text: str, forms: list[str]) -> int:
    normalized_text = normalize(text)
    total = 0
    for form in {normalize(item).strip() for item in forms if str(item).strip()}:
        total += len(re.findall(r"(?<!\w)" + re.escape(form) + r"(?!\w)", normalized_text))
    return total


def tokens(text: str) -> list[str]:
    return re.findall(r"(?u)\b[\w-]+\b", normalize(text))


def introduced_patterns(source_text: str, edited_text: str) -> dict[str, list[dict[str, Any]]]:
    source_tokens = tokens(source_text)
    edited_tokens = tokens(edited_text)
    result: dict[str, list[dict[str, Any]]] = {
        "tokens": [],
        "bigrams": [],
        "trigrams": [],
    }

    source_counts = Counter(source_tokens)
    edited_counts = Counter(edited_tokens)
    for token, after in edited_counts.items():
        before = source_counts[token]
        delta = after - before
        if (
            not token.isdigit()
            and token not in FUNCTION_WORDS
            and after >= 3
            and delta >= 2
        ):
            result["tokens"].append(
                {"pattern": token, "before": before, "after": after, "added": delta}
            )

    for size, label in ((2, "bigrams"), (3, "trigrams")):
        source_ngrams = Counter(
            " ".join(source_tokens[index : index + size])
            for index in range(len(source_tokens) - size + 1)
        )
        edited_ngrams = Counter(
            " ".join(edited_tokens[index : index + size])
            for index in range(len(edited_tokens) - size + 1)
        )
        for pattern, after in edited_ngrams.items():
            before = source_ngrams[pattern]
            delta = after - before
            if after >= 2 and delta >= 2:
                result[label].append(
                    {
                        "pattern": pattern,
                        "before": before,
                        "after": after,
                        "added": delta,
                    }
                )

    for values in result.values():
        values.sort(key=lambda item: (-item["added"], -item["after"], item["pattern"]))
    return result


def coverage_metrics(items: list[dict[str, Any]]) -> dict[str, Any]:
    covered_before = sum(item["before"] > 0 for item in items)
    covered_after = sum(item["after"] > 0 for item in items)
    median_groups = [
        item
        for item in items
        if item["median"] is not None and float(item["median"]) > 0
    ]
    median_sum = sum(float(item["median"]) for item in median_groups)
    depth_before = (
        sum(min(item["before"], float(item["median"])) for item in median_groups)
        / median_sum
        if median_sum
        else 0.0
    )
    depth_after = (
        sum(min(item["after"], float(item["median"])) for item in median_groups)
        / median_sum
        if median_sum
        else 0.0
    )
    return {
        "groups": len(items),
        "median_groups": len(median_groups),
        "covered_before": covered_before,
        "covered_after": covered_after,
        "width_before": round(covered_before / len(items), 4) if items else 0.0,
        "width_after": round(covered_after / len(items), 4) if items else 0.0,
        "depth_before": round(depth_before, 4),
        "depth_after": round(depth_after, 4),
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    source_text = read_text_auto(args.source)
    edited_text = read_text_auto(args.text)
    depth = depth_rows(args.depth)
    groups = lsi_groups(args.lsi, depth, args.breadth_limit)
    phrases = phrase_rows(args.phrases)
    irrelevant = irrelevant_rows(args.irrelevant)
    width_words = simple_word_list(args.width_words)
    relevant_words = simple_word_list(args.relevant_groups)
    relevant_keys = {normalize_header(item) for item in relevant_words}

    lsi_result = []
    for group in groups:
        before = count_forms(source_text, group["forms"])
        after = count_forms(edited_text, group["forms"])
        median = group["median"]
        if median is not None and median > 0:
            status = (
                "over" if after > median else "at" if after == median else "under"
            )
        else:
            added = max(0, after - before)
            status = (
                "breadth-over"
                if added > 1
                else "covered"
                if after > 0
                else "uncovered"
            )
        lsi_result.append(
            {
                **group,
                "median": clean_number(median),
                "analyzer_current": clean_number(group["analyzer_current"]),
                "before": before,
                "after": after,
                "status": status,
            }
        )

    depth_result = []
    minimum_result = []
    for item in depth:
        delta = item["delta"]
        before = count_forms(source_text, item["forms"])
        after = count_forms(edited_text, item["forms"])
        repeats = item["repeats"]
        synchronized = repeats is not None and before == repeats
        maximum = item["maximum"]
        if delta is not None and delta < 0:
            target = (
                maximum
                if synchronized and maximum is not None
                else max(0.0, before - abs(delta))
            )
        elif maximum is not None and before > maximum:
            target = maximum
        else:
            target = None
        if target is not None:
            status = "at" if after == target else "above" if after > target else "below"
            depth_result.append(
                {
                    **item,
                    "repeats": clean_number(repeats),
                    "minimum": clean_number(item["minimum"]),
                    "maximum": clean_number(maximum),
                    "delta": clean_number(delta),
                    "before": before,
                    "after": after,
                    "target": clean_number(target),
                    "synchronized": synchronized,
                    "status": status,
                }
            )
        minimum = item["minimum"]
        is_relevant_minimum = (
            not relevant_keys or normalize_header(item["word"]) in relevant_keys
        )
        if minimum is not None and minimum > 0 and is_relevant_minimum:
            minimum_result.append(
                {
                    "word": item["word"],
                    "forms": item["forms"],
                    "minimum": clean_number(minimum),
                    "before": before,
                    "after": after,
                    "status": "at-least" if after >= minimum else "below",
                }
            )

    phrase_result = []
    for item in phrases:
        before = count_forms(source_text, [item["phrase"]])
        after = count_forms(edited_text, [item["phrase"]])
        if before or after:
            phrase_result.append(
                {
                    **item,
                    "median": clean_number(item["median"]),
                    "analyzer_current": clean_number(item["analyzer_current"]),
                    "before": before,
                    "after": after,
                    "status": (
                        "over"
                        if after > item["median"]
                        else "at"
                        if after == item["median"]
                        else "under"
                    ),
                }
            )

    irrelevant_result = []
    for item in irrelevant:
        before = count_forms(source_text, [item["form"]])
        after = count_forms(edited_text, [item["form"]])
        irrelevant_result.append(
            {
                **item,
                "before": before,
                "after": after,
                "status": "at" if after <= item["target"] else "above",
            }
        )

    width_result = []
    for word in width_words:
        before = count_forms(source_text, [word])
        after = count_forms(edited_text, [word])
        width_result.append(
            {
                "word": word,
                "before": before,
                "after": after,
                "status": "covered" if after > 0 else "uncovered",
            }
        )

    warnings = []
    for item in lsi_result:
        analyzer = item["analyzer_current"]
        if analyzer is not None and analyzer != item["before"]:
            warnings.append(
                f"LSI {item['word']}: файл={item['before']}, анализатор={analyzer}"
            )
    for item in depth_result:
        if not item["synchronized"]:
            warnings.append(
                f"Глубина {item['word']}: таблица несинхронна с исходным текстом"
            )
    for item in irrelevant_result:
        reported = item["reported_current"]
        if reported is not None and reported != item["before"]:
            warnings.append(
                f"Нерелевантное {item['form']}: файл={item['before']}, "
                f"анализатор={reported}"
            )

    raw_metrics = coverage_metrics(lsi_result)
    matched_relevant_keys = {
        normalize_header(item["word"])
        for item in lsi_result
        if normalize_header(item["word"]) in relevant_keys
    }
    filtered_groups = [
        item
        for item in lsi_result
        if normalize_header(item["word"]) in relevant_keys
    ]
    filtered_metrics = coverage_metrics(filtered_groups) if relevant_keys else None
    for missing in sorted(relevant_keys - matched_relevant_keys):
        warnings.append(f"Релевантная группа не найдена в первых строках: {missing}")

    patterns = introduced_patterns(source_text, edited_text)
    source_facts = fact_tokens(source_text)
    edited_facts = fact_tokens(edited_text)
    missing_facts = sorted(source_facts - edited_facts)
    added_facts = sorted(edited_facts - source_facts)
    source_yo = len(re.findall("[\u0401\u0451]", source_text))
    edited_yo = len(re.findall("[\u0401\u0451]", edited_text))

    return {
        "source": str(args.source),
        "text": str(args.text),
        "lsi": str(args.lsi),
        "depth": str(args.depth) if args.depth else None,
        "phrases": str(args.phrases) if args.phrases else None,
        "irrelevant": str(args.irrelevant) if args.irrelevant else None,
        "width_words": str(args.width_words) if args.width_words else None,
        "relevant_groups": str(args.relevant_groups)
        if args.relevant_groups
        else None,
        "summary": {
            "lsi_groups": len(lsi_result),
            "breadth_limit": args.breadth_limit,
            "median_groups": raw_metrics["median_groups"],
            "lsi_over": sum(item["status"] == "over" for item in lsi_result),
            "breadth_over": sum(
                item["status"] == "breadth-over" for item in lsi_result
            ),
            "covered_before": raw_metrics["covered_before"],
            "covered_after": raw_metrics["covered_after"],
            "raw_width_before": raw_metrics["width_before"],
            "raw_width_after": raw_metrics["width_after"],
            "raw_depth_before": raw_metrics["depth_before"],
            "raw_depth_after": raw_metrics["depth_after"],
            "filtered_groups": filtered_metrics["groups"]
            if filtered_metrics
            else None,
            "filtered_covered_before": filtered_metrics["covered_before"]
            if filtered_metrics
            else None,
            "filtered_covered_after": filtered_metrics["covered_after"]
            if filtered_metrics
            else None,
            "filtered_width_before": filtered_metrics["width_before"]
            if filtered_metrics
            else None,
            "filtered_width_after": filtered_metrics["width_after"]
            if filtered_metrics
            else None,
            "filtered_depth_before": filtered_metrics["depth_before"]
            if filtered_metrics
            else None,
            "filtered_depth_after": filtered_metrics["depth_after"]
            if filtered_metrics
            else None,
            "negative_groups": len(depth_result),
            "negative_above": sum(item["status"] == "above" for item in depth_result),
            "minimum_groups": len(minimum_result),
            "minimum_below": sum(item["status"] == "below" for item in minimum_result),
            "irrelevant_groups": len(irrelevant_result),
            "irrelevant_above": sum(
                item["status"] == "above" for item in irrelevant_result
            ),
            "width_words": len(width_result),
            "width_covered_before": sum(
                item["before"] > 0 for item in width_result
            ),
            "width_covered_after": sum(item["after"] > 0 for item in width_result),
            "introduced_token_flags": len(patterns["tokens"]),
            "introduced_frame_flags": len(patterns["bigrams"])
            + len(patterns["trigrams"]),
            "source_yo": source_yo,
            "edited_yo": edited_yo,
            "missing_fact_tokens": len(missing_facts),
            "added_fact_tokens": len(added_facts),
            "warnings": len(warnings),
        },
        "lsi_groups": lsi_result,
        "negative_groups": depth_result,
        "minimum_groups": minimum_result,
        "phrases_present": phrase_result,
        "irrelevant_groups": irrelevant_result,
        "width_word_groups": width_result,
        "introduced_patterns": patterns,
        "fact_tokens": {
            "missing": missing_facts,
            "added": added_facts,
        },
        "warnings": warnings,
    }


def print_report(result: dict[str, Any]) -> None:
    summary = result["summary"]
    print(
        "SUMMARY"
        f"\tlsi_groups={summary['lsi_groups']}"
        f"\tlsi_over={summary['lsi_over']}"
        f"\tbreadth_over={summary['breadth_over']}"
        f"\tcovered={summary['covered_before']}->{summary['covered_after']}"
        f"\twidth={summary['raw_width_before']}->{summary['raw_width_after']}"
        f"\tdepth={summary['raw_depth_before']}->{summary['raw_depth_after']}"
        f"\tnegative_groups={summary['negative_groups']}"
        f"\tnegative_above={summary['negative_above']}"
        f"\tminimum_below={summary['minimum_below']}"
        f"\tirrelevant_above={summary['irrelevant_above']}"
        f"\twidth_words={summary['width_covered_before']}"
        f"->{summary['width_covered_after']}/{summary['width_words']}"
        f"\tintroduced_flags={summary['introduced_token_flags']}"
        f"\tframe_flags={summary['introduced_frame_flags']}"
        f"\tyo={summary['source_yo']}->{summary['edited_yo']}"
        f"\tfacts_missing={summary['missing_fact_tokens']}"
        f"\tfacts_added={summary['added_fact_tokens']}"
        f"\twarnings={summary['warnings']}"
    )
    if summary["filtered_groups"] is not None:
        print(
            "FILTERED"
            f"\tgroups={summary['filtered_groups']}"
            f"\tcovered={summary['filtered_covered_before']}"
            f"->{summary['filtered_covered_after']}"
            f"\twidth={summary['filtered_width_before']}"
            f"->{summary['filtered_width_after']}"
            f"\tdepth={summary['filtered_depth_before']}"
            f"->{summary['filtered_depth_after']}"
        )
    print("LSI\tgroup\tmedian\tbefore\tafter\tstatus")
    ordered = sorted(result["lsi_groups"], key=lambda item: item["breadth_rank"])
    for item in ordered:
        if item["before"] != item["after"] or item["status"] in {
            "over",
            "breadth-over",
        }:
            print(
                "LSI"
                f"\t{item['word']}\t{item['median']}"
                f"\t{item['before']}\t{item['after']}\t{item['status']}"
            )
    print("DEPTH\tgroup\ttarget\tbefore\tafter\tstatus\tsynchronized")
    for item in result["negative_groups"]:
        print(
            "DEPTH"
            f"\t{item['word']}\t{item['target']}"
            f"\t{item['before']}\t{item['after']}\t{item['status']}"
            f"\t{str(item['synchronized']).lower()}"
        )
    print("MINIMUM\tgroup\tminimum\tbefore\tafter\tstatus")
    for item in result["minimum_groups"]:
        if item["before"] != item["after"] or item["status"] == "below":
            print(
                "MINIMUM"
                f"\t{item['word']}\t{item['minimum']}"
                f"\t{item['before']}\t{item['after']}\t{item['status']}"
            )
    print("IRRELEVANT\tform\ttarget\tbefore\tafter\tstatus")
    for item in result["irrelevant_groups"]:
        if item["before"] or item["after"]:
            print(
                "IRRELEVANT"
                f"\t{item['form']}\t{item['target']}"
                f"\t{item['before']}\t{item['after']}\t{item['status']}"
            )
    print("WIDTH\tword\tbefore\tafter\tstatus")
    for item in result["width_word_groups"]:
        if item["before"] != item["after"]:
            print(
                "WIDTH"
                f"\t{item['word']}\t{item['before']}"
                f"\t{item['after']}\t{item['status']}"
            )
    for token in result["fact_tokens"]["missing"]:
        print(f"FACT\tmissing\t{token}")
    for token in result["fact_tokens"]["added"]:
        print(f"FACT\tadded\t{token}")
    for warning in result["warnings"]:
        print(f"WARNING\t{warning}")
    for label in ("tokens", "bigrams", "trigrams"):
        for item in result["introduced_patterns"][label]:
            print(
                "INTRODUCED"
                f"\t{label}\t{item['pattern']}"
                f"\t{item['before']}\t{item['after']}\t+{item['added']}"
            )


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--source", required=True, type=Path, help="Исходный UTF-8 текст")
    result.add_argument("--text", required=True, type=Path, help="Проверяемый UTF-8 текст")
    result.add_argument("--lsi", required=True, type=Path, help="LSI XLSX")
    result.add_argument("--depth", type=Path, help="Таблица глубины XLSX")
    result.add_argument("--phrases", type=Path, help="Таблица N-грамм XLSX")
    result.add_argument(
        "--irrelevant",
        type=Path,
        help="Файл точных нерелевантных слов анализатора",
    )
    result.add_argument(
        "--width-words",
        type=Path,
        help="Дополнительный список слов для ширины",
    )
    result.add_argument(
        "--relevant-groups",
        type=Path,
        help="Проверенный список релевантных основных LSI-групп",
    )
    result.add_argument(
        "--breadth-limit",
        type=int,
        default=150,
        choices=range(140, 151),
        metavar="140..150",
        help="Число первых разных LSI-групп для проверки ширины (по умолчанию 150)",
    )
    result.add_argument("--json", action="store_true", help="Вывести JSON вместо отчета")
    result.add_argument("--json-output", type=Path, help="Дополнительно сохранить JSON")
    result.add_argument(
        "--strict",
        action="store_true",
        help="Вернуть код 1 при нарушении обязательных ограничений",
    )
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        result = analyze(args)
    except (OSError, ValueError, zipfile.BadZipFile, ET.ParseError) as error:
        print(f"ERROR\t{error}", file=sys.stderr)
        return 2
    if args.json_output:
        args.json_output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_report(result)
    failed = (
        result["summary"]["lsi_over"]
        or result["summary"]["breadth_over"]
        or result["summary"]["negative_above"]
        or result["summary"]["irrelevant_above"]
        or result["summary"]["edited_yo"]
        or result["summary"]["missing_fact_tokens"]
        or result["summary"]["added_fact_tokens"]
    )
    return 1 if args.strict and failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
