#!/usr/bin/env python3
"""Проверка Title и Description на длину, вхождения ключа, повторы и отрицательную релевантность.
Использование: python3 check_meta.py --title "..." --desc "..." --key "главный ключ" [--type article|commercial] [--h1 "..."]
"""
import argparse, re, sys
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")
try:
    import pymorphy3; M = pymorphy3.MorphAnalyzer()
    lem = lambda w: M.parse(w)[0].normal_form
except Exception:
    lem = lambda w: w

JUNK = ['главная', 'добро пожаловать', 'каталог', 'официальный сайт', 'описание, цены, характеристики', 'фото, отзывы', 'лучший', 'самый']
INFO = ['как выбрать', 'своими руками', 'что такое', 'что это', 'история', 'как сделать', 'инструкция']
COMM = ['купить', 'цена', 'цены', 'заказать', 'недорого', 'доставка', 'стоимость']
STOP = set('и в во на с со к ко по о об от для из за до у а но или же ли не как что это'.split())

def words(s): return [w for w in re.findall(r'[a-zа-яё0-9-]+', s.lower())]

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--title', required=True); p.add_argument('--desc', default='')
    p.add_argument('--key', required=True); p.add_argument('--type', default='article', choices=['article', 'commercial'])
    p.add_argument('--h1', default='')
    a = p.parse_args(); warn = []
    t, d = a.title.strip(), a.desc.strip()
    print(f'Title: {len(t)} знаков | Description: {len(d)} знаков')
    if not 45 <= len(t) <= 65: warn.append(f'Title {len(t)} знаков — вне ориентира 45–65')
    if d and not 120 <= len(d) <= 160: warn.append(f'Description {len(d)} знаков — вне ориентира 120–160')
    kl = [lem(w) for w in words(a.key)]
    tl = [lem(w) for w in words(t)]
    hits = sum(1 for i in range(len(tl)) if tl[i:i+len(kl)] == kl)
    print(f'Вхождений главного ключа в Title: {hits}')
    if hits == 0: warn.append('Главного ключа нет в Title')
    if hits > 2: warn.append('Главный ключ в Title больше 2 раз — переспам')
    pos = ' '.join(words(t)).find(' '.join(words(a.key)))
    if pos > 30: warn.append('Главный ключ далеко от начала Title')
    rep = [w for w, n in Counter(x for x in tl if x not in STOP and len(x) > 2).items() if n > 1]
    if rep: warn.append('Повторы в Title: ' + ', '.join(rep))
    low = t.lower()
    for j in JUNK:
        if j in low: warn.append(f'Мусорное/шаблонное: «{j}»')
    bad = INFO if a.type == 'commercial' else COMM
    for j in bad:
        if j in low: warn.append(f'Маркер чужого интента для {a.type}: «{j}»')
    if t.count(',') >= 3: warn.append('Много запятых — возможно перечисление разнородных тем')
    if '!' in t or '!' in d: warn.append('Восклицательный знак — рекламный стиль')
    if re.search(r'\b[А-ЯЁA-Z]{4,}\b', t + ' ' + d): warn.append('Слова капслоком')
    if d and t.lower() == d.lower(): warn.append('Description совпадает с Title')
    if d:
        dl = set(lem(w) for w in words(d) if w not in STOP)
        share = len(set(tl) & dl) / max(1, len(set(tl)))
        if share > 0.8: warn.append('Description почти дублирует Title')
        if len(re.findall(r'[.!?]', d)) == 0: warn.append('Description без законченного предложения')
    if a.h1 and a.h1.strip().lower() == low: warn.append('Title дословно совпадает с H1')
    if a.h1 and a.h1.strip().lower() != low:
        stop = set('и в во на с со к по о об от до из за для не но а или что это как ли он она они его её ее их вы ваш вашему ваш свой такое такой простыми словами'.split())
        keyw = set(re.findall(r'[a-zа-яё0-9]+', a.key.lower()))
        sig = lambda s: {w for w in re.findall(r'[a-zа-яё0-9]+', s.lower()) if w not in stop and w not in keyw}
        tw, hw = sig(low), sig(a.h1)
        if tw and len(tw & hw) / len(tw) > 0.6:
            warn.append(f'Title слишком похож на H1: {len(tw & hw)} из {len(tw)} значимых слов (без ключа и служебных) совпадают — {", ".join(sorted(tw & hw))}; переформулировать, добавить другой ключ или угол')
    print('\n'.join('⚠ ' + w for w in warn) if warn else 'Замечаний нет. Проверьте вручную по чек-листу: обещания Title есть в тексте, LSI из ГАР, читаемость.')

if __name__ == '__main__':
    main()
