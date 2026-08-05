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
    "checked_query": "\"пример запроса\"",
    "frequency_type": "phrase",
    "frequency": 2400,
    "region": "Россия",
    "device": "all",
    "tab": "Топы запросов",
    "period": "последний месяц",
    "checked_at": "2026-08-05",
    "evidence_status": "MEASURED",
    "source": "Яндекс Вордстат",
    "evidence_locator": "https://wordstat.yandex.ru/... или export.csv:строка 12"
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
  ]
}
```

Требования:

- `status`: `PASS`, `NEEDS_INPUT` или `NO_ELIGIBLE_KEYWORD`;
- при `PASS` обязательны все поля главного ключа и частота 1000–5000;
- при `PASS` тип частоты — `phrase`, строка проверки в точности повторяет фразу в кавычках, а `rejected_candidates` содержит минимум двух полностью описанных кандидатов с теми же условиями измерения и причиной отклонения;
- при `NEEDS_INPUT` главный ключ равен `null`, а категории пусты;
- `categories` содержит ID 1–21 ровно по одному разу;
- категория содержит хотя бы одну группу либо непустой `na_reason`;
- итог `PASS` содержит хотя бы одну семантическую группу;
- `canonical` уникален без учета регистра, `ё/е` и повторных пробелов;
- разрешенные доказательные статусы: `MEASURED`, `USER_PROVIDED`, `ESTIMATED`, `UNKNOWN`.
- каждая включенная группа имеет источник, локатор, доказательство связи и статус `INCLUDED`;
- `excluded_terms` при наличии содержит термин, причину и тип исключения (`HOMONYM`, `OTHER_INTENT`, `NOISE`, `DUPLICATE`, `UNSUPPORTED`).
