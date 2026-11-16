# Библиотека визуальных промптов для ChatGPT, Flux и Midjourney

Современные генеративные модели (ChatGPT с поддержкой DALL-E 3 / 4o Image, Flux 1.1 Pro, Midjourney v6) качественно генерируют типографику и инфографику без необходимости ручной верстки или устаревших скриптов.

---

## 1. Правила стабильной генерации текста на изображениях

1. **Кавычки обязательны:** Любой текст, который должен появиться на изображении, заключается в строгие двойные кавычки: `"ЗАГОЛОВОК"`.
2. **Лимит слов на плашке:** Чем короче текст, тем выше вероятность 100% корректного рендеринга. Оптимально: заголовок из 2–5 слов, подзаголовок из 3–6 слов.
3. **Контраст и негативное пространство:** В промпте обязательно задается чистое пространство (negative space, breathing room не менее 20–30%) и контрастный фон под текст.
4. **Соотношение сторон:**
   - Для Pinterest: вертикальное соотношение **2:3** (1000×1500 px или `--ar 2:3`).
   - Для Threads / каруселей: квадрат **1:1** (1080×1080 px) или вертикаль **4:5** (1080×1350 px).

---

## 2. 6 рабочих визуальных архетипов для Pinterest и соцсетей

### Архетип 1: Split Layout (Фото сверху + Информационная карточка снизу)
*Идеально для: экспертных разборов, гайдов, анонсов лид-магнитов.*

**Формула для ChatGPT / DALL-E 3:**
```text
A vertical 2:3 pin design with a clean split layout. 
Top half: A high-end editorial candid photo of [описание сцены: modern minimalist desk with notebook, coffee, and soft window light / confident expert working on laptop]. Neutral muted color palette (beige, warm grey, sage green). Soft diffused morning lighting.
Bottom half: Solid off-white card background with crisp modern typography. 
Top small tag in bold uppercase: "[РУБРИКА]".
Main huge bold headline centered in clean sans-serif Russian text: "[ГЛАВНЫЙ ЗАГОЛОВОК ИЗ 3-4 СЛОВ]".
Small subtitle below: "[ПОДЗАГОЛОВОК С ПОЛЬЗОЙ ИЗ 4-5 СЛОВ]".
Professional graphic design, generous whitespace, zero clutter, high aesthetic.
```

**Формула для Flux / Midjourney v6:**
```text
Clean graphic design 2:3 vertical layout, split composition. Top 50% is a cinematic photograph of [scene description], soft natural lighting, muted aesthetic tones. Bottom 50% is a minimalist paper textured card displaying large crisp bold typography reading "[ТЕКСТ ЗАГОЛОВКА]". Modern editorial layout, balanced margins, hyper-clean swiss typography --ar 2:3 --style raw
```

---

### Архетип 2: Dark Editorial Minimalist (Темный люксовый минимализм)
*Идеально для: прорывных инсайтов, разборов ошибок, высокого чека и твердого бизнеса.*

**Формула для ChatGPT / DALL-E 3:**
```text
A sleek vertical 2:3 graphic with a deep matte dark charcoal (#121214) background. 
Minimalist premium editorial style. Subtle micro-textures like fine film grain or dark brushed stone.
In the center, large high-contrast typography in pure white and warm metallic gold accents.
Big bold title in Russian: "[ГЛАВНЫЙ ТЕЗИС ИЛИ ЗАБЛУЖДЕНИЕ]".
Below, in smaller clean typography: "[ОДНО ПРЕДЛОЖЕНИЕ ОБЪЯСНЕНИЯ]".
At the bottom, a neat small badge: "[ПОШАГОВЫЙ РАЗБОР ВНУТРИ]".
Balanced composition, luxury tech magazine aesthetic, perfectly aligned.
```

**Формула для Flux / Midjourney v6:**
```text
Minimalist dark theme graphic layout, vertical 2:3 ratio. Deep matte graphite background with subtle studio shadows. Elegant high-contrast bold white typography displaying the exact Russian words: "[ТЕКСТ ЗАГОЛОВКА]". Subtle neon or bronze glowing accent line beneath the text. High-end fintech branding, swiss graphic design, flawless clean layout --ar 2:3
```

---

### Архетип 3: Numbered Checklist / Cheat Sheet (Инфографика-шпаргалка)
*Идеально для: списков, инструкций, максимального числа сохранений (Saves).*

**Формула для ChatGPT / DALL-E 3:**
```text
A vertical 2:3 educational infographic pin on a light cream background (#F8F7F4). 
Structured grid layout with 4 clean horizontal cards or rows.
Top header: A bold high-impact headline in deep navy blue: "[5 ШАГОВ К РЕЗУЛЬТАТУ]".
Each row contains:
Row 1: Number "01" in a neat rounded circle, next to Russian text: "[ШАГ 1]".
Row 2: Number "02", next to Russian text: "[ШАГ 2]".
Row 3: Number "03", next to Russian text: "[ШАГ 3]".
Row 4: Number "04", next to Russian text: "[ШАГ 4]".
Bottom footer with a subtle bookmark icon and text: "[СОХРАНИТЕ ЧЕК-ЛИСТ]".
Minimalist UI card design, soft pastel accents, ultra-crisp readable vector-like typography.
```

---

### Архетип 4: "X vs Y" / Comparison (Контрастное сравнение до/после или миф/реальность)
*Идеально для: ломки стереотипов, отстройки от конкурентов, вовлечения.*

**Формула для ChatGPT / DALL-E 3:**
```text
A vertical 2:3 comparison pin design divided into two distinct columns or vertical panels.
Left side (Muted / Problem): Soft light grey background with a subtle red accent icon. Header: "[КАК ДЕЛАЮТ ВСЕ]". Bullet text: "[ОШИБКА ИЛИ СЛИВ БЮДЖЕТА]".
Right side (High Contrast / Solution): Vibrant mint green or rich dark navy background with a bright checkmark icon. Header: "[КАК РАБОТАЕТ В 2026]". Bullet text: "[СИСТЕМНЫЙ ПОДХОД]".
Top central header spanning both sides: "[СТАРЫЙ vs НОВЫЙ МЕТОД]".
Clean modern product design comparison, crisp typography, clear visual hierarchy.
```

---

### Архетип 5: Visual Step Pipeline (Схема связки или воронки)
*Идеально для: объяснения архитектуры воронок, нейросетевых связок и процессов.*

**Формула для ChatGPT / DALL-E 3:**
```text
A clean vertical 2:3 architectural diagram pin. Light warm grey background.
A visual 3-step vertical pipeline connected by sleek thin minimalist arrows:
Step 1: Rounded card with text "[ТРАФИК ИЗ ПИНТЕРЕСТ / THREADS]".
Arrow pointing down.
Step 2: Rounded card with text "[КЕЙС-МАГНИТ С РАЗБОРОМ]".
Arrow pointing down.
Step 3: High-contrast highlighted card with text "[ТРИПВАЕР И ПЕРВАЯ ПРОДАЖА]".
Clean tech-startup flowchart style, subtle drop shadows, readable sans-serif Russian text.
```

---

### Архетип 6: Warm Paper & Editorial Serif (Теплый книжно-журнальный стиль)
*Идеально для: психологов, коучей, экспертов по мышлению, авторских блогов.*

**Формула для ChatGPT / DALL-E 3:**
```text
A vertical 2:3 editorial aesthetic design with authentic warm linen paper texture and natural soft organic shadows of plant leaves in the corner.
Refined typography: large elegant serif font in deep espresso brown (#2B2118).
Headline centered: "[ТОЧНАЯ ЦИТАТА ИЛИ МЫСЛЬ АВТОРА]".
Bottom clean italic note: "[ПРАКТИКА И РАЗБОР В ОПИСАНИИ]".
Gentle, peaceful, intellectual mood, sophisticated layout, ample breathing room.
```

---

## 3. Промпт для реверс-инжиниринга визуальных референсов

Если у автора уже есть референс понравившегося пина, этот промпт отправляется в ChatGPT или Claude вместе с прикрепленным изображением:

```text
Проанализируй прикрепленное изображение как арт-директор и специалист по prompt engineering.
Разложи его на визуальные параметры и составь:
1. Цветовую палитру (основной фон, акценты, контраст).
2. Композицию и сетку (расположение элементов, соотношение фото и текста, поля).
3. Готовый промпт на английском языке для генерации точной копии этого визуального стиля в ChatGPT/Flux. 
Все текстовые заголовки оставь на русском языке в строгих двойных кавычках.
```
