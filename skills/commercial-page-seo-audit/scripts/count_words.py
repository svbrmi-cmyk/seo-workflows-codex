#!/usr/bin/env python3
"""Считает вхождения слов (все словоформы) в теле текста.

Использование:
  python3 count_words.py FILE "пол=пол|пола|полу|полом|полы|полов|полам|полами|полах" "ковролин=ковролин\\w*"

Каждый аргумент после файла: метка=регулярное выражение (без границ, они добавляются).
Если в файле есть строка '---', считается только текст после первой такой строки (мета-шапка пропускается).
URL внутри markdown-ссылок не считаются, анкоры считаются.
"""
import re
import sys

LETTER = "А-Яа-яЁёA-Za-z"


def main() -> None:
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    text = open(sys.argv[1], encoding="utf-8").read()
    if "\n---\n" in text:
        text = text.split("\n---\n", 1)[1]
    text = re.sub(r"\]\([^)]*\)", "]", text)
    for spec in sys.argv[2:]:
        label, pattern = spec.split("=", 1)
        rx = re.compile(rf"(?<![{LETTER}])(?:{pattern})(?![{LETTER}])", re.I)
        hits = rx.findall(text)
        print(f"{label}: {len(hits)}")
        for i, line in enumerate(text.splitlines(), 1):
            n = len(rx.findall(line))
            if n:
                print(f"  стр.{i} ×{n}: {line.strip()[:90]}")


if __name__ == "__main__":
    main()
