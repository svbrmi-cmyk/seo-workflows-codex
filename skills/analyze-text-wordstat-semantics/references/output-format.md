# Формат машинной проверки

Сохраните аудит в UTF-8 JSON. Минимальная структура:

```json
{
  "status": "PASS",
  "intent": {
    "primary": "informational",
    "summary": "Как решить задачу",
    "evidence": ["наблюдение 1", "наблюдение 2"]
  },
  "main_keyword": {
    "phrase": "пример запроса",
    "checked_query": "seed-фраза, по которой получена таблица",
    "frequency_type": "top_query",
    "frequency": 2400,
    "region": "Россия",
    "device": "all",
    "tab": "Топы запросов",
    "period": "последний месяц",
    "checked_at": "2026-08-05",
    "evidence_status": "MEASURED",
    "source": "Яндекс Вордстат",
    "evidence_locator": "https://wordstat.yandex.ru/... или export.csv:строка 12",
    "evidence_kind": "csv",
    "evidence_file": "C:/path/export.csv",
    "evidence_row": 12,
    "intent_fit": "high",
    "coverage_evidence": "Покрывает основной объект и задачу текста",
    "match_type": "exact_intent",
    "selection_constraint": "Диапазон частотности 1000–5000 задан пользователем"
  },
  "rejected_candidates": [],
  "categories": [
    {
      "id": 1,
      "name": "Основная тема и сущность",
      "na_reason": null,
      "groups": [
        {
          "canonical": "пример",
          "variants": ["вариант"],
          "source": "текст пользователя",
          "evidence_locator": "абзац 3",
          "evidence_status": "USER_PROVIDED",
          "relation_evidence": "Термин описывает основной объект текста",
          "relevance_status": "INCLUDED"
        }
      ]
    }
  ],
  "checks": {
    "single_intent_and_keyword": true,
    "frequency_in_range": true,
    "frequency_evidenced": true,
    "measurement_parameters_complete": true,
    "all_categories_accounted": true,
    "noise_removed": true,
    "groups_relevant": true,
    "group_evidence_complete": true
  },
  "handoff_summary": {
    "confirmed": ["подтверждено"],
    "estimated": ["оценено"],
    "unknown": [],
    "next_data": []
  }
}
```

Требования:

- `status`: `PASS`, `NEEDS_INPUT` или `NO_ELIGIBLE_KEYWORD`;
- при `PASS` обязательны все поля главного ключа и частота 1000–5000;
- при `PASS` тип частоты — `top_query`, `phrase` точно повторяет выбранную строку CSV, `checked_query` хранит seed-фразу выгрузки, а `rejected_candidates` содержит минимум двух полностью описанных кандидатов с теми же условиями измерения и причиной отклонения;
- при `NEEDS_INPUT` главный ключ равен `null`, а категории пусты;
- `categories` содержит ID 1–21 ровно по одному разу;
- категория содержит хотя бы одну группу либо непустой `na_reason`;
- итог `PASS` содержит хотя бы одну семантическую группу;
- `canonical` уникален без учета регистра, `ё/е` и повторных пробелов;
- разрешенные доказательные статусы: `MEASURED`, `USER_PROVIDED`, `ESTIMATED`, `UNKNOWN`.
- каждая включенная группа имеет источник, локатор, доказательство связи и статус `INCLUDED`;
- `excluded_terms` при наличии содержит термин, причину и тип исключения (`HOMONYM`, `OTHER_INTENT`, `NOISE`, `DUPLICATE`, `UNSUPPORTED`).
- `evidence_kind` принимает `csv`, `screenshot`, `api` или `url`; для CSV указаны существующий `evidence_file` и `evidence_row`, а валидатор локально сверяет строку;
- `checks` содержит восемь успешных проверок, `handoff_summary` — подтвержденное, оцененное, неизвестное и следующие данные.

## Markdown с вариантами запросов

Создать `<article-slug>-wordstat-queries.md`:

```markdown
# Подходящие запросы Wordstat для «Название материала»

## Параметры проверки

- Дата:
- Период: последние 30 дней
- Регион:
- Устройства:
- Источник: официальный Wordstat API Яндекса

## Основной интент

<Формулировка, подтверждённая текстом>

## Подходящие запросы

| Запрос | Частота | Роль | Релевантность | Применение |
|---|---:|---|---|---|
| <фраза> | <число> | основной / уточняющий / тематический родитель | точная / широкая с оговоркой | главный ключ / H1 / дополнительный запрос |

## Отклонённые направления

| Направление | Частота | Причина отказа |
|---|---:|---|
| <фраза> | <число либо N/A> | омоним / чужой интент / отсутствует в тексте / слишком широко |

## Итог

- Статус: `PASS` / `NO_ELIGIBLE_KEYWORD` / `NO_RELEVANT_QUERIES` / `NEEDS_INPUT`
- Главный ключ:
- Точный long-tail:
- Локальный JSON API: `<путь внутри D:\CODEX\outputs>`
```

Не включать секреты, заголовки авторизации, технические идентификаторы API, полный сырой ответ и исчерпывающий список шумовых ассоциаций.
