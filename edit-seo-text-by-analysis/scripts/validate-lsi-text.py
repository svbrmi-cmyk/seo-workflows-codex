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
    return str(value or "").casefold().replace("ё", "е")


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
            "repeats": ["повторы"],
            "maximum": ["максимум по рекомендациям"],
            "delta": ["добавить/удалить"],
        },
        "глубин",
    )
    if detected is None:
        raise ValueError(f"Не найдена таблица глубины в {path}")
    sheet, header_index, columns = detected
    result = []
    for row in sheet["rows"][header_index + 1 :]:
        word = str(value_at(row, columns["word"]) or "").strip()
        if not word:
            continue
        result.append(
            {
                "word": word,
                "forms": split_forms(value_at(row, columns["forms"])),
                "repeats": number(value_at(row, columns["repeats"])),
                "maximum": number(value_at(row, columns["maximum"])),
                "delta": number(value_at(row, columns["delta"])),
            }
        )
    return result


def lsi_groups(path: Path, depth: list[dict[str, Any]]) -> list[dict[str, Any]]:
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
    for row in sheet["rows"][header_index + 1 :]:
        word = str(value_at(row, columns["word"]) or "").strip()
        median = number(value_at(row, columns["median"]))
        if not word or median is None or median <= 0:
            continue
        link = relation_key(value_at(row, columns["link"]))
        forms = set(forms_by_link.get(link, set()))
        forms.add(word)
        forms.update(supplemental.get(normalize_header(word), []))
        result.append(
            {
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


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    source_text = args.source.read_text(encoding="utf-8")
    edited_text = args.text.read_text(encoding="utf-8")
    depth = depth_rows(args.depth)
    groups = lsi_groups(args.lsi, depth)
    phrases = phrase_rows(args.phrases)

    lsi_result = []
    for group in groups:
        before = count_forms(source_text, group["forms"])
        after = count_forms(edited_text, group["forms"])
        median = group["median"]
        status = "over" if after > median else "at" if after == median else "under"
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
    for item in depth:
        delta = item["delta"]
        if delta is None or delta >= 0:
            continue
        before = count_forms(source_text, item["forms"])
        after = count_forms(edited_text, item["forms"])
        repeats = item["repeats"]
        synchronized = repeats is not None and before == repeats
        if synchronized and item["maximum"] is not None:
            target = item["maximum"]
        else:
            target = max(0.0, before - abs(delta))
        status = "at" if after == target else "above" if after > target else "below"
        depth_result.append(
            {
                **item,
                "repeats": clean_number(repeats),
                "maximum": clean_number(item["maximum"]),
                "delta": clean_number(delta),
                "before": before,
                "after": after,
                "target": clean_number(target),
                "synchronized": synchronized,
                "status": status,
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

    covered_before = sum(item["before"] > 0 for item in lsi_result)
    covered_after = sum(item["after"] > 0 for item in lsi_result)
    median_sum = sum(float(item["median"]) for item in lsi_result)
    depth_before = (
        sum(min(item["before"], float(item["median"])) for item in lsi_result)
        / median_sum
        if median_sum
        else 0.0
    )
    depth_after = (
        sum(min(item["after"], float(item["median"])) for item in lsi_result)
        / median_sum
        if median_sum
        else 0.0
    )
    patterns = introduced_patterns(source_text, edited_text)

    return {
        "source": str(args.source),
        "text": str(args.text),
        "lsi": str(args.lsi),
        "depth": str(args.depth) if args.depth else None,
        "phrases": str(args.phrases) if args.phrases else None,
        "summary": {
            "lsi_groups": len(lsi_result),
            "lsi_over": sum(item["status"] == "over" for item in lsi_result),
            "covered_before": covered_before,
            "covered_after": covered_after,
            "raw_width_before": round(covered_before / len(lsi_result), 4)
            if lsi_result
            else 0.0,
            "raw_width_after": round(covered_after / len(lsi_result), 4)
            if lsi_result
            else 0.0,
            "raw_depth_before": round(depth_before, 4),
            "raw_depth_after": round(depth_after, 4),
            "negative_groups": len(depth_result),
            "negative_above": sum(item["status"] == "above" for item in depth_result),
            "introduced_token_flags": len(patterns["tokens"]),
            "introduced_frame_flags": len(patterns["bigrams"])
            + len(patterns["trigrams"]),
            "warnings": len(warnings),
        },
        "lsi_groups": lsi_result,
        "negative_groups": depth_result,
        "phrases_present": phrase_result,
        "introduced_patterns": patterns,
        "warnings": warnings,
    }


def print_report(result: dict[str, Any]) -> None:
    summary = result["summary"]
    print(
        "SUMMARY"
        f"\tlsi_groups={summary['lsi_groups']}"
        f"\tlsi_over={summary['lsi_over']}"
        f"\tcovered={summary['covered_before']}->{summary['covered_after']}"
        f"\twidth={summary['raw_width_before']}->{summary['raw_width_after']}"
        f"\tdepth={summary['raw_depth_before']}->{summary['raw_depth_after']}"
        f"\tnegative_groups={summary['negative_groups']}"
        f"\tnegative_above={summary['negative_above']}"
        f"\tintroduced_flags={summary['introduced_token_flags']}"
        f"\tframe_flags={summary['introduced_frame_flags']}"
        f"\twarnings={summary['warnings']}"
    )
    print("LSI\tgroup\tmedian\tbefore\tafter\tstatus")
    ordered = sorted(
        result["lsi_groups"],
        key=lambda item: (-float(item["median"]), normalize(item["word"])),
    )
    for item in ordered:
        if item["before"] != item["after"] or item["status"] == "over":
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
    result.add_argument("--json", action="store_true", help="Вывести JSON вместо отчёта")
    result.add_argument("--json-output", type=Path, help="Дополнительно сохранить JSON")
    result.add_argument(
        "--strict",
        action="store_true",
        help="Вернуть код 1 при превышении медианы или цели удаления",
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
    failed = result["summary"]["lsi_over"] or result["summary"]["negative_above"]
    return 1 if args.strict and failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
