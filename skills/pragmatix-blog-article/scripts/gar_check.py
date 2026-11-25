#!/usr/bin/env python3
"""Проверка текста по отчётам ГАР (глубина и LSI): переспам и недобор.
Использование: python3 gar_check.py ТЕКСТ.md [--deep gar_deep.xlsx] [--lsi gar_lsi.xlsx] [--min-median 2]
Текст очищается от URL в markdown-ссылках; подписи ссылок считаются как текст (как в ГАР).
"""
import argparse, re, sys
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")
import openpyxl
try:
    import pymorphy3; M = pymorphy3.MorphAnalyzer(); lem = lambda w: M.parse(w)[0].normal_form
except Exception:
    lem = lambda w: w

def tokens(path):
    t = open(path, encoding='utf-8').read()
    t = re.sub(r'\]\([^)]+\)', ']', t).lower()
    return re.findall(r'[a-zа-яё0-9]+(?:-[a-zа-яё0-9]+)*', t)

def deep(path, toks):
    ws = openpyxl.load_workbook(path, data_only=True)['Рекомендации по глубине']
    head = [str(h) for h in next(ws.iter_rows(max_row=1, values_only=True))]
    flat = Counter(x for t in toks for x in t.split('-')) + Counter(t for t in toks if '-' in t)
    median_fmt = 'Медиана' in head  # формат «по медиане»: Медиана, Текст рекомендации
    print('== Глубина (словоформы ГАР):', 'слово: в тексте [медиана / рекомендация по тексту]' if median_fmt else 'слово: в тексте [мин–макс]')
    hi, lo = [], []
    for r in ws.iter_rows(min_row=2, values_only=True):
        if not r[0]: continue
        forms = [f.strip() for f in str(r[1]).split(',')]
        n = sum(flat[f] for f in forms)
        if median_fmt:
            med, rec = r[head.index('Медиана')], r[head.index('Текст рекомендации')]
            top = max(med, rec)
            if n > top * 1.3 and n - top >= 2: hi.append(f'{r[0]}:{n}[{med}/{rec}]')
            elif n < min(med, rec): lo.append(f'{r[0]}:{n}[{med}/{rec}]')
        else:
            mn, mx = r[3], r[4]
            if n > mx: hi.append(f'{r[0]}:{n}[{mn}-{mx}]')
            elif n < mn: lo.append(f'{r[0]}:{n}[{mn}-{mx}]')
    print('ПЕРЕСПАМ:', ' '.join(hi) or 'нет'); print('НЕДОБОР:', ' '.join(lo) or 'нет')

def lsi(path, toks, minmed):
    ws = openpyxl.load_workbook(path, data_only=True)['Сводим формы слов']
    c = Counter(lem(x) if re.match('[а-яё]', x) else x for x in toks)
    miss, low, hi = [], [], []
    for r in ws.iter_rows(min_row=2, values_only=True):
        w, med, spam = r[0], r[5], r[6]
        if not w or med is None: continue
        n = c[lem(w)] if re.match('[а-яё]', w) else c[w]
        if med >= minmed and n == 0: miss.append(f'{w}({med})')
        elif med >= minmed and n < med: low.append(f'{w}:{n}/{med}')
        if n > spam and n - spam >= 2: hi.append(f'{w}:{n}>{spam}')
    print('== LSI (леммы): медиана ТОПа и порог переспама')
    print('НЕТ В ТЕКСТЕ:', ' '.join(miss) or 'нет'); print('НИЖЕ МЕДИАНЫ:', ' '.join(low) or 'нет'); print('ПЕРЕСПАМ (+2 и более):', ' '.join(hi) or 'нет')

if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('text'); p.add_argument('--deep'); p.add_argument('--lsi'); p.add_argument('--min-median', type=int, default=2)
    a = p.parse_args(); toks = tokens(a.text)
    if a.deep: deep(a.deep, toks)
    if a.lsi: lsi(a.lsi, toks, a.min_median)
