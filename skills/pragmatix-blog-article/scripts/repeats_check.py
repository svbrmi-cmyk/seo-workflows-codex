#!/usr/bin/env python3
"""Поиск повторов в тексте статьи: подсказки для самопроверки на смысловые петли.
Использование: python3 repeats_check.py ТЕКСТ.md [--n 4] [--near 2]

Печатает:
1) повторяющиеся словосочетания из N слов (по умолчанию 4) — кандидаты в дубли мыслей;
2) одинаковые значимые леммы, которые стоят в соседних предложениях (окно --near),
   чаще 2 раз — кандидаты в тавтологию («бизнеса… для бизнеса», «менеджеры… менеджеров»);
3) подряд идущие знаки «: … :» и «— … —» в одном предложении — кандидаты в неудачную пунктуацию.
Скрипт только подсказывает: решение о правке принимается по смыслу.
"""
import argparse, re, sys
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")
try:
    import pymorphy3; M = pymorphy3.MorphAnalyzer(); lem = lambda w: M.parse(w)[0].normal_form
except Exception:
    lem = lambda w: w

STOP = set('и в во на с со к ко по о об от до из у за для не ни но а или что это как то так же ли бы его ее её их он она они мы вы ты я который которая которые которое чтобы если когда где уже еще ещё только тоже также при без над под между через после перед там тут здесь всё все весь вся быть есть был была были может можно нужно стоит один одна одно свой своя свои такой такая такие этот эта эти тот та те какой какая какие каким'.split())

p = argparse.ArgumentParser(); p.add_argument('text'); p.add_argument('--n', type=int, default=4); p.add_argument('--near', type=int, default=2)
a = p.parse_args()
t = open(a.text, encoding='utf-8').read()
t = re.sub(r'\]\([^)]+\)', ']', t)            # URL в ссылках не считаем
body = re.sub(r'^#.*$', '', t, flags=re.M)     # заголовки не считаем

words = re.findall(r'[а-яёa-z0-9]+', body.lower())
grams = Counter(tuple(words[i:i + a.n]) for i in range(len(words) - a.n + 1))
rep = [' '.join(g) for g, c in grams.items() if c > 1 and not all(w in STOP for w in g)]
print(f'== Повторы из {a.n} слов:', '; '.join(rep) or 'нет')

sents = [s for s in re.split(r'(?<=[.!?])\s+|\n+', body) if s.strip()]
lems = [[lem(w) for w in re.findall(r'[а-яё]+', s.lower()) if len(w) > 3 and w not in STOP] for s in sents]
hits = []
for i in range(len(sents)):
    win = Counter(l for j in range(i, min(i + a.near, len(sents))) for l in lems[j])
    for l, c in win.items():
        if c > 2:
            hits.append(f'{l}×{c}: «{sents[i][:70]}…»')
print(f'== Одна лемма 3+ раза в {a.near} соседних предложениях:')
print('\n'.join(dict.fromkeys(hits)) or 'нет')

punct = [s[:90] for s in sents if s.count(':') > 1 or s.count(' — ') > 2]
print('== Предложения с двумя двоеточиями или тремя тире:')
print('\n'.join(punct) or 'нет')
