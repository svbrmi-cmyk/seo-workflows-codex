#!/usr/bin/env python3
"""Видимый объём текста и частоты заданных лемм и фраз.
Использование: python3 text_stats.py ТЕКСТ.md [--lemmas "ссылка,площадка"] [--phrases "потенциальных клиентов;целевой аудитории"]
"""
import argparse, re, sys
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")
try:
    import pymorphy3; M = pymorphy3.MorphAnalyzer(); lem = lambda w: M.parse(w)[0].normal_form
except Exception:
    lem = lambda w: w
p = argparse.ArgumentParser(); p.add_argument('text'); p.add_argument('--lemmas', default=''); p.add_argument('--phrases', default='')
a = p.parse_args(); t = open(a.text, encoding='utf-8').read()
v = re.sub(r'\]\([^)]+\)', ']', t); vis = re.sub(r'[*#\[\]>`]', '', v)
print('Видимый объём:', len(vis), 'знаков; файл:', len(t))
low = v.lower(); c = Counter(lem(w) for w in re.findall(r'[а-яё]+', low))
if a.lemmas: print('; '.join(f'{w}: {c[lem(w)]}' for w in a.lemmas.split(',') if w))
if a.phrases: print('; '.join(f'«{ph}»: {low.count(ph.lower())}' for ph in a.phrases.split(';') if ph))
