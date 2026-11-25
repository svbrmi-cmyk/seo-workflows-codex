#!/usr/bin/env python3
"""Проверка текста по стартовому списку слов заказчика.

Использование:
    python3 semantics_check.py WORDS.txt TOP_N START.md [OTHER.md ...] CURRENT.md

WORDS.txt  стартовый список слов (через пробел или по строкам, в порядке заказчика).
TOP_N      сколько первых слов списка сверять с ориентиром 10 употреблений (обычно 15).
START.md   первая сданная версия текста: эталон охвата списка.
CURRENT.md последняя версия; между ними можно передать промежуточные версии.

Кириллица считается по леммам (pymorphy3, все варианты разбора, «ё» = «е»),
латиница и слова через дефис (seo, geo, ai-поиске) по точной форме.
Печатает охват списка по каждой версии, частоты первых TOP_N слов,
слова, выпавшие относительно START, и слова, не использованные в CURRENT.
"""
import re
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")

import pymorphy3

MORPH = pymorphy3.MorphAnalyzer()


def lemmas(word):
    return {p.normal_form.replace("ё", "е") for p in MORPH.parse(word.replace("ё", "е"))}


def stats(path, words):
    text = open(path, encoding="utf-8").read().lower().replace("ё", "е")
    counts = Counter()
    for token in re.findall(r"[a-zа-я]+", text):
        for lem in lemmas(token):
            counts[lem] += 1
    res = {}
    for w in words:
        if "-" in w or re.match(r"[a-z]", w):
            res[w] = len(re.findall(r"(?<![a-zа-я])" + re.escape(w) + r"(?![a-zа-я])", text))
        else:
            res[w] = max(counts[l] for l in lemmas(w))
    return res, len(open(path, encoding="utf-8").read())


def main():
    words_path, top_n, *files = sys.argv[1:]
    top_n = int(top_n)
    words = open(words_path, encoding="utf-8-sig").read().split()
    results = [stats(f, words) for f in files]
    for f, (r, n) in zip(files, results):
        print(f"{f}: знаков {n}, слов из списка {sum(1 for w in words if r[w])} из {len(words)}")
    cur = results[-1][0]
    start = results[0][0]
    print("\nПервые", top_n, "(ориентир — 10, если это естественно):")
    print("  " + ", ".join(f"{w} {cur[w]}{' LOW' if cur[w] < 10 else ''}" for w in words[:top_n]))
    print("\nВыпали относительно стартовой версии:",
          ", ".join(w for w in words if start[w] and not cur[w]) or "нет")
    if len(results) > 2:
        previous = results[-2][0]
        print("Выпали в последнем круге:",
              ", ".join(w for w in words if previous[w] and not cur[w]) or "нет")
    print("Не использованы в текущей версии:",
          ", ".join(w for w in words if not cur[w]) or "нет")


if __name__ == "__main__":
    main()
