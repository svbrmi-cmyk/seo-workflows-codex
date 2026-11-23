#!/usr/bin/env python3
"""Сверка оптимизированной статьи с исходником.

Использование:
    python check_article.py original.md optimized.md [--key "главный запрос"] [--lsi lsi.txt]

lsi.txt — по одному слову/фразе на строку.
Выделение вставок **…** и [+ …] перед сравнением снимается.
"""
import argparse
import difflib
import re
import sys
from collections import Counter

WORD = re.compile(r"[A-Za-zА-Яа-яЁё0-9]+")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def strip_markup(text):
    text = re.sub(r"\[\+\s*(.*?)\]", r"\1", text, flags=re.S)
    return text.replace("**", "")


def headings(text):
    return [m.group(2).strip() for m in re.finditer(r"^(#{1,6})\s+(.+)$", text, re.M)]


def numbers(text):
    return Counter(re.findall(r"\d+(?:[.,]\d+)?\s?%?", text))


def stem(word, n=5):
    # Грубая морфология: совпадение по первым n буквам
    w = word.lower().replace("ё", "е")
    return w[:n] if len(w) > n else w


def count_phrase(text, phrase):
    words = [stem(w) for w in WORD.findall(text)]
    target = [stem(w) for w in WORD.findall(phrase)]
    if not target:
        return 0
    return sum(1 for i in range(len(words) - len(target) + 1) if words[i:i + len(target)] == target)


def sentences(text):
    plain = re.sub(r"^#{1,6}\s+.*$", "", text, flags=re.M)
    return [s.strip() for s in re.split(r"(?<=[.!?…])\s+|\n{2,}", plain) if s.strip()]


def removed_fragments(orig, opt):
    """Фрагменты исходника, которых нет в оптимизированной версии (должны только добавлять)."""
    a, b = WORD.findall(orig.lower()), WORD.findall(opt.lower())
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    out = []
    for tag, i1, i2, _, _ in sm.get_opcodes():
        if tag in ("delete", "replace"):
            out.append(" ".join(a[i1:i2]))
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("original")
    p.add_argument("optimized")
    p.add_argument("--key", help="главный запрос")
    p.add_argument("--lsi", help="файл со списком LSI")
    p.add_argument("--max-words", type=int, default=25)
    args = p.parse_args()

    orig = strip_markup(read(args.original))
    opt_raw = read(args.optimized)
    opt = strip_markup(opt_raw)
    problems = 0

    print("== Цифры ==")
    lost = numbers(orig) - numbers(opt)
    if lost:
        problems += 1
        print("ПОТЕРЯНЫ:", ", ".join(f"{k.strip()} ×{v}" for k, v in lost.items()))
    else:
        print("ок, все цифры исходника на месте")

    print("\n== Заголовки ==")
    ho, hn = headings(orig), headings(opt)
    if len(ho) != len(hn):
        problems += 1
        print(f"ЧИСЛО ИЗМЕНИЛОСЬ: было {len(ho)}, стало {len(hn)}")
    for a, b in zip(ho, hn):
        mark = "  " if a == b else "~ "
        print(f"{mark}{a}  →  {b}" if a != b else f"{mark}{a}")
        if a != b and not all(w in b.lower() for w in WORD.findall(a.lower())):
            problems += 1
            print("   ВНИМАНИЕ: из заголовка пропали слова исходника")

    print("\n== Удалённые/заменённые фрагменты исходника ==")
    rem = [r for r in removed_fragments(orig, opt) if r]
    if rem:
        problems += 1
        for r in rem[:30]:
            print("-", r)
        if len(rem) > 30:
            print(f"... и ещё {len(rem) - 30}")
    else:
        print("ок, исходный текст сохранён полностью (только добавления)")

    chars = len(opt)
    print(f"\n== Объём == было {len(orig)} знаков, стало {chars} (+{chars - len(orig)})")

    if args.key:
        n = count_phrase(opt, args.key)
        lo, hi = max(1, round(3 * chars / 6000)), max(2, round(6 * chars / 6000))
        flag = "" if lo <= n <= hi else f"  ВНЕ ОРИЕНТИРА {lo}–{hi}"
        print(f"\n== Главный ключ «{args.key}» == {n} раз (было {count_phrase(orig, args.key)}){flag}")

    if args.lsi:
        print("\n== LSI ==")
        for line in read(args.lsi).splitlines():
            term = line.strip()
            if not term:
                continue
            n = count_phrase(opt, term)
            flag = "  ПЕРЕСПАМ" if n > 2 else ("  не вошло" if n == 0 else "")
            print(f"{term}: {n}{flag}")

    print(f"\n== Длинные предложения (> {args.max_words} слов) ==")
    long_ = [s for s in sentences(opt) if len(WORD.findall(s)) > args.max_words
             and s not in sentences(orig)]
    for s in long_:
        print(f"- [{len(WORD.findall(s))}] {s[:160]}")
    if not long_:
        print("ок (длинные предложения исходника не считаются)")

    print("\n== Частые слова (топ-10, длиной от 5 букв) ==")
    freq = Counter(stem(w) for w in WORD.findall(opt) if len(w) >= 5)
    print(", ".join(f"{w}…×{c}" for w, c in freq.most_common(10)))

    print(f"\nИТОГ: {'есть замечания — исправь до выдачи' if problems else 'критичных расхождений нет'}")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
