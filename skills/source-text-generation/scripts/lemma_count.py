#!/usr/bin/env python3
"""Частоты слов из списка заказчика в тексте по леммам.

Использование:
    python3 lemma_count.py TEXT.md WORDS.txt TOP [--exempt LEMMA,LEMMA]

TEXT.md   готовый текст.
WORDS.txt слова заказчика через пробел или по одному на строке, в порядке списка.
TOP       леммы первых 15 подходящих слов через запятую (норма не меньше 10).
--exempt  леммы из запросов и H1, на которые не действует лимит 1-2.

Все формы слова считаются вместе, «ё» приравнивается к «е».
Печатает только слова, которые есть в тексте или входят в TOP:
LOW  - слово из TOP встречается меньше 10 раз;
HIGH - остальное слово встречается больше 2 раз.
Нужен pymorphy3: pip install pymorphy3.
"""
import collections
import re
import sys

import pymorphy3

MORPH = pymorphy3.MorphAnalyzer()


def lemma(word):
    return MORPH.parse(word.replace("ё", "е"))[0].normal_form.replace("ё", "е")


def main():
    args = sys.argv[1:]
    exempt = set()
    if "--exempt" in args:
        i = args.index("--exempt")
        exempt = set(args[i + 1].split(","))
        del args[i:i + 2]
    text_path, words_path, top_arg = args
    top = [w.strip() for w in top_arg.split(",") if w.strip()]

    text = open(text_path, encoding="utf-8").read().lower().replace("ё", "е")
    tokens = re.findall(r"[а-я]+", text)
    counts = collections.Counter(lemma(t) for t in tokens)
    print(f"слов в тексте: {len(tokens)}")

    seen = []
    for w in open(words_path, encoding="utf-8").read().split():
        lm = lemma(w.lower())
        if lm in seen:
            continue
        seen.append(lm)
        n = counts.get(lm, 0)
        mark = ""
        if lm in top:
            mark = "TOP" + (" LOW" if n < 10 else "")
        elif n > 2:
            mark = "EXEMPT" if lm in exempt else "HIGH"
        if n or lm in top:
            print(f"{w:22}{lm:20}{n:4} {mark}")


if __name__ == "__main__":
    main()
