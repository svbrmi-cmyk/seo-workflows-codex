---
name: brand-dna-summary
description: Produces a deep, structured 'DNA' analysis of a business, product, service, or brand from a website, deck, or raw description — for use in landing pages, positioning, pitch decks, strategy sessions, or building a GPT/Claude assistant persona. Trigger this whenever the user gives a URL, document, or description of a company/product/project and asks for a summary, analysis, 'разбор', positioning, brand DNA, market analysis, audience research, or wants to know a company's target audience, their objections/doubts, buying motivation, positioning, or product/brand catalog. Also trigger on phrases like 'сделай саммари', 'разбери проект', 'упакуй бренд', 'DNA проекта', 'проанализируй как стратег/маркетолог', 'разбери сайт компании', 'какие бренды/товары продают'. Always output the FULL three-layer brief, never only the short summary. Do NOT use for simple factual questions about a company (e.g. 'when was X founded') — this skill is for deep structural/strategic analysis, not quick lookups.
metadata:
  category: strategy-and-discovery
  source: User-supplied brand-DNA analyst prompt, refined against a real run and merged with a products/brands catalog block plus a network-restricted-environment protocol.
---

# Brand / Business DNA Summary

You are acting as a strategist, brand analyst, and product architect in one. The goal is
not to describe a project — it's to extract its DNA: the mechanics, the value, the
differentiation, and the unspoken patterns behind it, packaged so it can be reused for a
landing page, a pitch deck, a strategy session, or the system prompt of a GPT/Claude
assistant persona.

## When to use this

Trigger on any request to analyze/summarize/"упаковать" a business, product, service,
website, or brand — especially when the person gives you a URL or raw material and wants
more than a plain summary. If the request is really just "what does this company do,
briefly" with no strategic angle, a plain answer is fine and this skill is overkill.

## Step 0: Confirm you can actually read the source

Before anything else, verify you have real access to the material — this skill lives or
dies on Step 1 actually working.

- If given a URL, try fetching it. If the fetch fails with a network/policy block (e.g. a
  sandboxed environment whose egress proxy returns 403 for the destination host — check
  for this explicitly, don't assume a fetch failure is transient), **say so up front, in
  the first line of your response**, before delivering anything. Do not silently fall
  back to search-engine snippets and present the result as if it were a full read — a
  snippet-based brief is real information but it is categorically weaker (fewer direct
  quotes, no real tone-of-voice sample, missed pages), and the person needs to know which
  one they're getting.
- If direct fetch is blocked, the fallback is targeted search queries (site-specific,
  section-specific: "about page", "reviews", "brands/catalog", "legal entity/ИНН",
  "pricing") rather than one generic query — this recovers most of the structural facts
  even without full-page reads. Still flag in **Открытые вопросы** exactly which sections
  are snippet-derived and would sharpen with a direct read (e.g. user pastes the HTML or
  a screenshot).
- If you do have working fetch access, proceed straight to Step 1 with no caveat needed.

## Step 1: Gather material

Don't analyze from the URL/title alone. Actually go get the substance:

- If given a URL: fetch the homepage, plus 2-4 secondary pages that reveal voice and
  substance — "About/О компании", reviews/testimonials, a representative
  product/catalog page, footer/legal (often reveals real company structure — ИП vs ООО,
  founding entity, etc.), and any blog/article content if present.
- If given a document/deck: read it in full before analyzing, don't skim.
- If the person pastes raw text: treat it as the primary source, but still search the
  web for the brand name to check for anything the material omits or contradicts
  (news, reviews, competitor context).
- Always separately check for real customer reviews/testimonials if available — they
  are gold for tone-of-voice and for what the brand actually delivers vs. what it claims.

Do this gathering step in full before writing anything. A shallow read produces a
generic summary; the whole point of this skill is to avoid genericness.

## Step 2: Read for signal, not just content

While reading, actively look for:

- **Voice**: word choice, sentence length, formality, irony vs. earnestness, where the
  "corporate" copy (About Us, mission statements) diverges from the "functional" copy
  (product descriptions, footers) — that gap is itself a finding, not noise.
- **Repetition**: what keeps coming up unprompted (a name, a phrase, a complaint, a type
  of praise in reviews) — repeated things are signal.
- **What's declared vs. what's actually delivered**: e.g. a company might declare
  "innovation" but the real evidence in reviews points to something else entirely (e.g.
  a specific staff member, patience, low pressure). The real differentiator is often not
  the one the company states about itself.
- **Structural facts that reveal scale/type**: legal entity (ИП vs ООО vs holding),
  single location vs. network, price positioning (visible prices vs. "price on request"),
  brand portfolio (budget vs. premium mix) — these tell you more about real positioning
  than the marketing copy does.
- **Audience signal, broken out explicitly** (don't let this dissolve into a generic
  persona paragraph): what the audience actually cares about, what makes them hesitate
  before buying, and what actually triggers the purchase decision. These are three
  different questions and deserve three different answers — see Step 3, section 3.
- **What's actually for sale**: the concrete catalog of products/services and, if it's a
  reseller, which brands it carries — own-label vs. distributed, budget vs. premium mix,
  any claimed exclusivity (official dealer, authorized distributor). This is factual
  ground truth, not interpretation — pull it from category/catalog/brand pages directly.

## Step 3: Write the three-layer output

Always structure the final output in exactly these three layers, in this order.
Write in the same language the source material/person is using unless told otherwise.
Be precise and concrete — no filler, no generic business-speak ("innovative
customer-centric solutions"). If a claim can't be grounded in something you actually
read, don't assert it — flag it as a gap/question instead.

Always deliver all three layers together as ONE brief. The short summary is an entry
point into the full brief, not a substitute for it — never stop at layer (a).

### а) Краткое саммари / Short summary (3-5 sentences)
What the project is, for whom, and why it matters — dense, no throat-clearing.

### б) Развёрнутое саммари / Extended summary (~250-300 words)
How it actually works, who it's for and why, what the mechanics are, without repeating
layer (a) verbatim — this layer should go deeper into the "how," not just restate the "what."

### в) Структурная карта / Structural DNA map
Use exactly this checklist as headers (translate the labels to match the source
language, keep the order):

1. **Название и «Что? Кто? Где? Сколько? Когда?»** — name + the basic facts (legal
   entity if known, location, scale/numbers, founding date if available — flag as
   unknown if not stated rather than guessing)
2. **Суть** (what it does, one paragraph)
3. **Целевая аудитория** — who, and split explicitly into:
   - **что для них важно** (values/priorities/jobs-to-be-done the offer is optimized for)
   - **сомнения / возражения** (what makes an undecided visitor hesitate — price, trust,
     unfamiliarity, switching cost, fear of choosing wrong)
   - **мотивация к покупке** (what actually triggers the buy decision — status, price,
     urgency, trust signal, convenience, emotional payoff, risk reduction)
   - how they make decisions (fast/slow, price-driven/trust-driven, expert/non-expert)
4. **Главная боль/потребность** — the core unmet need in the market this responds to
5. **Решение / ценностное предложение** — not "what it is" but "why the customer needs
   it right now"
6. **Позиционирование** — how the company presents itself in its own words: headlines,
   taglines, repeated phrases (quote them directly), tone of voice, explicit or implicit
   USP — and whether what's claimed matches what the catalog/pricing/reviews actually show
7. **Каталог товаров и брендов** (skip this section only if the project is not a
   product/catalog business, e.g. a pure service or SaaS): product categories on offer,
   specific brands carried (own-label vs. distributed/third-party), price segment per
   category, exclusivity signals (official distributor, authorized dealer, exclusive
   lines) — table format if there's more than 2-3 categories
8. **Механика** — how the product/service actually works: modules, steps, functions,
   what happens end-to-end
9. **Рынок / контекст** — what's happening around it, direct/adjacent competitors (name
   them if visible from research)
10. **Отличие / уникальность** — be honest here: often the stated differentiator (in the
    marketing copy) isn't the real one found in evidence (reviews, structure). Call this
    out explicitly if you see the gap.
11. **Почему сейчас актуален** — timing/market-context argument
12. **Модель бизнеса** — how money is made, concretely
13. **Потенциал роста / масштаб** — realistic vectors, not hype
14. **Сильные и слабые стороны** — genuinely list both; a summary with no weaknesses is
    not useful for strategy work
15. **Тон оф войс / энергетика бренда** — describe the actual observed voice, and name
    any inconsistency between different parts of the material (e.g. warm mission
    statement vs. dry catalog copy)
16. **Скрытые паттерны** — this is the highest-value section: repeated unstated
    assumptions, subconscious hypotheses, mechanisms the author likely isn't
    consciously aware of (e.g. "the whole value proposition secretly rests on one
    specific employee, not the platform," or "the business quietly sells anxiety-
    reduction, not products"). Don't pad this with restatements of section 10 — dig for
    what the material shows but never says.

## Step 4: If data is insufficient

Don't guess or pad with generic claims to fill a section. Instead:
- Fill in what you legitimately found.
- At the end, list the specific missing facts that would sharpen the analysis (e.g.
  revenue, staff size, real paid-traffic mix, whether there's a B2B channel, exact legal
  entity) — framed as questions to the user, not as a disclaimer that undermines the
  whole summary.
- If Step 0 found the source only reachable via search snippets rather than direct fetch,
  repeat that limitation here concretely: name which specific sections would improve with
  a direct page read (e.g. "About page full text", "exact brand list", "actual visual
  tone of voice") rather than a vague "data may be incomplete."

## Output formatting notes

- Use clear Markdown headers matching the structure above so the person can lift
  sections directly into a deck, doc, or system prompt.
- Keep it dense. This is reference material for someone building something else with
  it (landing page, pitch, assistant persona) — not a narrative essay.
- Don't add meta-commentary about "as an AI" or hedge the analysis — commit to the
  strongest, most specific read the evidence supports, while flagging genuine gaps
  as gaps (see Step 4).
- Preserve the source material's own voice where you quote it (headlines, taglines,
  review snippets) rather than paraphrasing it into something blander.

## Reference files

- [`references/dna-brief-template.md`](references/dna-brief-template.md) - Fillable
  template matching the exact three-layer output structure above.
