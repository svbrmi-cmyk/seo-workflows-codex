---
name: visual-traffic-prompts
description: >
  Органический трафик и визуальные промпты для блогеров и экспертов. Связка визуального SEO-поисковика Pinterest и разговорного механизма Threads с генерацией промптов для ChatGPT, Flux и Midjourney. Создает пины с высоким CTR, инфографику, карусели и обложки с выверенной кириллической типографикой и переливом трафика в воронку первой продажи. Триггеры: "visual-traffic-prompts", "pinterest", "threads", "промпты для картинок", "пины для блога", "трафик из пинтерест", "визуал для тредов", "инфографика для блога".
---

# Visual Traffic & Prompts: Органический трафик и визуальный конвейер

## 1. Целевая задача (Objective)
Генерация связки органического трафика (Pinterest SEO + Threads) и точных промптов для создания визуальных материалов (ChatGPT, Flux, Midjourney) с переливом в воронку первой продажи.

## 2. Контекстная призма (Stance & Context)
- **Функциональная роль:** Специалист по органическому трафику: находить цепляющие темы для Pinterest и Threads и писать точные промпты для генерации картинок.
- **Входящий контекст:** High Concept из [expert-brand-core](file:///d:/Antigravity/communitus/.agents/skills/expert-brand-core/SKILL.md), офферы из [funnel-first-sale](file:///d:/Antigravity/communitus/.agents/skills/funnel-first-sale/SKILL.md).
- **Критерии качества:** Высокий поисковый CTR пинов, нативная интеграция текстовых слоев в промпты, сквозная связь с кейс-магнитом.

---

## Связи с архитектурой проекта

- **Базовое позиционирование:** берет High Concept и драматический конфликт из [expert-brand-core](file:///d:/Antigravity/communitus/.agents/skills/expert-brand-core/SKILL.md).
- **Монетизация трафика:** переводит посетителей пинов и веток на Кейс-магнит и Трипваер из [funnel-first-sale](file:///d:/Antigravity/communitus/.agents/skills/funnel-first-sale/SKILL.md).
- **Детокс текстов:** очищает заголовки и посты через [expert-humaniser](file:///d:/Antigravity/communitus/.agents/skills/expert-humaniser/SKILL.md).

---

## 4 фазы работы скилла

### Фаза 1: Сбор поисковых ключей и архитектура досок (Pinterest)
1. Определение ниши и целевого сегмента автора.
2. Формирование поисковой матрицы (20–30 ключей по 2–3 слова в 4–5 рубриках).
3. Проектирование досок: 3–4 основные поисковые доски + 1–2 широкие охватные.
4. Детали и правила: [pinterest-seo-and-boards.md](file:///d:/Antigravity/communitus/.agents/skills/visual-traffic-prompts/references/pinterest-seo-and-boards.md).

### Фаза 2: Разговорные ветки и кастдев-хуки (Threads)
1. Выбор цели публикации: `subscribe` (конверсия в воронку), `discovery` (спор и охват) или `brand` (ценности и позиция).
2. Формирование хука (первые 2 строки) без шаблонных клише.
3. Добавление авторского первого комментария (Reply-Bait) для разгона обсуждения.
4. Детали и правила: [threads-conversational-engine.md](file:///d:/Antigravity/communitus/.agents/skills/visual-traffic-prompts/references/threads-conversational-engine.md).

### Фаза 3: Генерация визуальных промптов для ИИ
1. Подбор подходящего визуального архетипа под задачу:
   - Split Layout (эстетичное фото + контрастная плашка).
   - Dark Editorial Minimalist (темный стиль высокого чека).
   - Numbered Checklist (инфографика-шпаргалка под сохранения).
   - "X vs Y" / Comparison (контрастное сравнение).
   - Visual Step Pipeline (схема связки или воронки).
   - Warm Paper & Editorial Serif (текстурный журнальный стиль).
2. Сборка готового промпта на английском языке со строгим выделением кириллических заголовков в двойные кавычки `"..."`.
3. Готовые формулы: [prompt-archetypes-chatgpt-flux.md](file:///d:/Antigravity/communitus/.agents/skills/visual-traffic-prompts/references/prompt-archetypes-chatgpt-flux.md).

### Фаза 4: Мост в воронку первой продажи
1. Формирование описания пина с поисковым ключом и кнопкой-ссылкой на лид-магнит.
2. Настройка шапки профиля и закрепленного треда в Threads со ссылкой на Telegram-бота.
3. Разметка deep link меток для отслеживания окупаемости трафика.
4. Детали и правила: [funnel-bridge-templates.md](file:///d:/Antigravity/communitus/.agents/skills/visual-traffic-prompts/references/funnel-bridge-templates.md).

---

## Формат итогового пакета (Output Package)

По запросу пользователя скилл выдает готовый комплект для запуска:

```markdown
### 1. Пакет для Pinterest:
- **Доска:** [Поисковое название доски]
- **Заголовок пина (Title):** [До 100 знаков, ключ в начале]
- **Описание (Description):** [150-300 знаков с пользой и CTA]
- **Текстовый оверлей:** [2-4 слова крупно]
- **Промпт для ChatGPT / Flux:** [Готовый английский промпт с кириллицей в кавычках]
- **Ссылка назначения:** [Ссылка на бота с меткой источника]

### 2. Пакет для Threads:
- **Цель поста:** [discovery / subscribe / brand]
- **Текст поста:** [Хук + контекст + конкретный вопрос]
- **Reply-Bait (первый комментарий):** [Запуск диалога или ссылка]
```
