---
name: research-brand-category-products
description: Research a brand from its name and a retailer brand/category URL and produce a clear Russian brand-and-product brief. Use when Codex must study what the retailer actually sells, how the brand officially positions itself, what product categories, collections, series and lines it makes, what the brand is known for in authoritative sources, how its category-level products differ from alternatives, and which verified features create practical buyer advantages—without turning the result into a SKU catalog or a compliance audit.
---

# Research Brand, Categories and Product Lines

Use this as the primary workflow for brand-and-product research from:

- a brand name;
- a retailer brand or category URL.

The required result is a **clear brand brief**, not a product-card audit. Answer these
questions directly:

1. What does the retailer page show and sell under this brand?
2. How does the brand officially present and position itself?
3. What does the brand manufacture or offer by product category?
4. Which collections, series and product lines organize the range?
5. What is the brand known for according to credible independent or specialist sources?
6. How do its product categories differ from comparable brands?
7. Which verified features and technologies create practical buyer advantages?

Research categories, collections, series and lines. Use individual products only as
examples that prove a broader finding. Do not organize the report around SKUs.

## Research tools and source order

Use `scripts/perplexity_search.py` as the primary discovery tool after opening the
user-supplied retailer URL directly:

```text
python scripts/perplexity_search.py "precise research or verification query"
```

The script reads `PERPLEXITY_API_KEY` and returns JSON with an answer and source URLs.
Treat its answer as discovery, not proof.

Use this sequence:

1. Open and study the supplied retailer page directly.
2. Identify the brand's official site and open it directly.
3. Use Perplexity to discover official documents, interviews, trade publications,
   reputable specialist sources and category competitors.
4. Open important discovered pages directly before relying on them.
5. Use general web search as fallback when:
   - the retailer or official page cannot be read;
   - Perplexity misses categories or collections;
   - Perplexity returns an irrelevant namesake;
   - direct evidence contradicts the discovery answer;
   - authoritative independent coverage remains incomplete.
6. Record important access limitations and contradictions, but do not let retrieval
   diagnostics dominate the final brief.

Never silently replace Sancos with Sanaks, or another brand with a similar name.
Validate the domain, logo/name, product type and article conventions before accepting a
source.

If `PERPLEXITY_API_KEY` is absent or the script cannot run, report the blocker. Do not
claim that Perplexity was used when it was not.

## Evidence hierarchy

Prefer sources in this order:

1. official brand/manufacturer site, catalogs, manuals and certificates;
2. supplied retailer page and its category pages;
3. official regional distributor;
4. established trade media, professional publications, exhibition or award sites,
   certification databases and credible business sources;
5. established specialist retailers for assortment and local availability;
6. review datasets and installer sources for repeated experience patterns.

Use evidence labels internally:

- `[direct]` — page opened and read;
- `[document]` — catalog, manual, certificate or data sheet read;
- `[snippet]` — only a search-result snippet was available;
- `[inference]` — cautious consequence derived from verified facts.

Do not treat repeated retailer copy as independent confirmation. Do not use generic SEO
articles to establish what a brand is famous for.

## Phase 1: Understand the retailer page

Study the supplied page as the local assortment boundary. Capture:

- how the retailer describes the brand;
- which product categories and subcategories are present;
- visible collections or series;
- the relative emphasis of the assortment;
- meaningful configuration breadth: sizes, mounting types, finishes or use cases;
- price positioning when it is clearly observable;
- notable gaps between the retailer and official brand range.

Count products or category shares only when the page exposes reliable counts and the
numbers help explain the assortment. Do not make reconciliation tables the center of
the report.

Do not enumerate all products. Check enough representative cards to understand each
category and verify recurring features.

## Phase 2: Study the official brand

On the official brand or manufacturer site, determine:

- the brand's own positioning and target customer;
- the promised design, engineering, price or service level;
- brand history, geography and company identity when verifiable;
- the complete category architecture;
- collection, series and line structure;
- named technologies, materials, mechanisms, component suppliers and design concepts;
- warranties, service and documentation by category;
- whether the brand offers coordinated cross-category solutions.

Separate:

- **official positioning** — how the brand describes itself;
- **verified fact** — what primary evidence establishes;
- **unsupported marketing language** — claims without technical or independent support.

Do not infer manufacturing country from an Italian collection name, design style,
distributor address or retailer's “country of brand” field. If origin is unclear, say
so briefly.

## Phase 3: Determine what the brand is known for

Search beyond the official site. Prioritize:

- established industry media;
- professional architecture and design publications;
- major exhibitions and award databases;
- credible company profiles and interviews;
- certification and registry records;
- established specialist retailers with original editorial content;
- sufficiently large, deduplicated review datasets when reputation or defects matter.

Look for evidence of:

- recognizable design language or signature collections;
- category specialization;
- patented or named engineering;
- notable collaborations, awards or exhibition presence;
- reputation among designers, installers or buyers;
- long-running strengths or recurring weaknesses.

If authoritative independent coverage is sparse, state:

> The brand is visible in retail and distributor sources, but broad independent
> recognition was not established in the checked scope.

Never substitute advertising repetition for fame.

## Phase 4: Analyze categories, collections and lines

Organize the core research by product category. For every relevant category explain:

- what the brand offers;
- the main collections, series or lines;
- how those lines differ from one another;
- recurring materials, mechanisms, formats and finishes;
- category-wide features versus model-specific options;
- installation, compatibility or care constraints;
- the supported buyer benefit.

Use this reasoning chain:

`verified feature → practical consequence → buyer scenario → limitation`

Example:

`thermostat with 38 °C safety stop → reduces accidental temperature changes
→ useful for a family bathroom → still depends on correct pressure and installation`

Mark consequences as `[inference]` when not stated directly.

Do not generalize a feature from one model to a whole category unless:

- the official category or collection page says it is shared; or
- several representative products across the line confirm it.

## Phase 5: Find real differences and advantages

Compare at the category or collection level, not as a random SKU-versus-SKU table.

For each important category:

1. Define the comparable segment and buyer scenario.
2. Select several credible same-segment alternatives.
3. Compare the exact feature, line breadth, configuration choice, documentation,
   service or price position.
4. Classify the result:
   - **real differentiator** — materially uncommon and well supported;
   - **useful advantage** — buyer-relevant but available from multiple brands;
   - **industry standard** — common and not a reason to prefer the brand alone;
   - **not established** — evidence is insufficient.

Do not force a fixed competitor denominator when it adds noise. Name the competitors
and evidence basis clearly enough for the reader to understand the comparison.

An advantage may be a combination rather than an exclusive technology, for example:

- unusually broad size coverage within one coherent furniture line;
- coordinated finishes across mixers, showers and accessories;
- clearer technical documentation than peers;
- a useful combination of filter connection, flexible spout and multiple flow modes;
- stronger local stock, warranty or service.

Do not call anything “unique,” “exclusive,” “best” or “premium” unless the evidence
supports that exact conclusion.

## Phase 6: Write the brief

Read [references/report-template.md](references/report-template.md) before drafting.

Write in Russian unless the user requests another language. Lead with conclusions.
Keep sourcing visible but secondary to the narrative.

The brief must contain:

1. executive summary;
2. what the retailer page shows;
3. official brand profile and positioning;
4. what the brand makes;
5. category, collection and line analysis;
6. what the brand is known for;
7. differences from competitors;
8. real features and buyer advantages;
9. common features that are not differentiators;
10. limitations, contradictions and open questions;
11. concise ready-to-use brand brief.

Use compact tables only when they improve comparison. Do not include by default:

- a full product catalog;
- a long SKU evidence table;
- a claim-by-claim audit register;
- exhaustive source-retrieval logs;
- arithmetic that does not improve the brand conclusion.

## Quality gate

Before saving, verify:

- the report answers all seven core questions at the top of this skill;
- the retailer page and official site are both clearly represented;
- the official positioning is not presented as independent fact;
- “known for” is supported by authoritative external evidence or explicitly marked as
  not established;
- every store category in scope is covered at a useful level;
- collections, series and lines are explained, not merely listed;
- SKU evidence remains subordinate to category findings;
- model-specific features are not generalized;
- differences are separated into real differentiators, useful advantages and industry
  standards;
- buyer benefits follow from verified mechanisms;
- origin, warranty and technical conflicts remain visible but concise;
- the final section can be used as a practical brand brief without reading the research
  process.

Save the result under `D:\CODEX\outputs` unless the user specifies another destination.
