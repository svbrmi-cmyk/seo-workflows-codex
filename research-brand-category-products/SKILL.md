---
name: research-brand-category-products
description: Research and fact-check a brand's products using a supplied brand name and an online-store category URL. Use when Codex must map the brand assortment actually sold in one store category, find precise product features, technologies, series and specifications, compare them with same-segment alternatives, distinguish genuine differentiators from industry standards, translate verified details into buyer benefits, and produce a source-tagged report without invented facts.
---

# Research Brand Category Products

Accept two required inputs:

- brand name;
- online-store category URL.

Treat the store page as the boundary of the assortment under study, not as sufficient
evidence for every brand claim. Produce the most complete report the available evidence
supports. Never fill a gap with memory, inference presented as fact, or an
industry-typical characteristic.

Read [references/report-template.md](references/report-template.md) before drafting the
final result.

## 1. Establish scope and access

Open the supplied category URL and identify:

- store and market/region;
- category and any active filters;
- whether the page is brand-filtered;
- access date;
- whether product cards, filters and pagination are readable directly.

Check access separately for the store, official manufacturer, official regional
representative and other important sources.

Label evidence:

- `[direct]` — the page itself was opened and read;
- `[document]` — an official catalog, certificate or manual was read;
- `[snippet]` — only a search-result snippet was available;
- `[user-supplied]` — supplied by the user and not yet independently verified.

State access limitations before findings. Do not silently treat snippets as direct
evidence.

## 2. Map the store assortment

Enumerate only the named brand's products present in the supplied store category.
Handle pagination, lazy loading, variants and subcategories.

Record for every visible product:

- exact product name;
- SKU/article/model code;
- series or collection;
- product subtype;
- price and availability when visible;
- product-card URL;
- relevant visible specifications.

Report both:

- the store's displayed counter;
- the independently enumerated number of unique products.

Deduplicate by SKU/article first, then canonical product URL, then exact model identity.
Do not merge finish, size or configuration variants when the store sells them as
distinct SKUs. Explain the deduplication rule used.

If displayed and enumerated counts differ by no more than 3%, label the difference
possible catalog noise and explain it. Above 3%, recount and flag the discrepancy.

Use the mapped assortment to define research priorities: cover every series found, and
investigate the most represented or technically diverse subtypes first. Never research
unrelated brand categories unless needed for context and clearly marked out of scope.

## 3. Build the source map

Find and distinguish:

1. official manufacturer site;
2. official site for the relevant country or regional representative;
3. official catalogs, manuals, certificates and product data sheets;
4. the supplied store's product cards;
5. two or more established specialist retailers carrying the same models;
6. same-segment competitor sources needed to test differentiation;
7. registries, installer sources and review datasets when relevant.

Use the official source for brand history, production geography, named technologies,
series architecture and certifications. Use store and retailer cards to confirm what is
actually sold locally, not to establish unsupported corporate claims.

Before treating sources as independent confirmations, compare their wording. Identical
or near-identical descriptions copied from one supplier feed count as one evidence
chain. Record the likely common origin.

Prefer exact product/model pages to generic brand pages. Record publication/update date
when available and always record access date.

## 4. Atomize and verify claims

Convert every candidate statement into one atomic, checkable claim. Separate combined
sentences into:

- identity claims: brand, manufacturer, legal entity;
- dates and geography;
- product/series/SKU names;
- materials and component brands;
- mechanisms and named technologies;
- numeric specifications, tolerances and test cycles;
- standards, certificates and protection classes;
- warranty and service terms;
- catalog and assortment counts.

For every claim, capture the exact supporting passage or table value, source URL,
evidence label and access date. Preserve units and conditions. Do not generalize a
model-specific feature to the whole brand or series without explicit evidence.

Classify each claim exactly as:

- **confirmed**;
- **contradicted**;
- **unverifiable from available evidence**.

For contradictions, show both statements and offer a safe replacement formulation.
When sources conflict, prefer the more primary, model-specific and recent source, but
report the conflict rather than silently choosing.

Verify geographic and legal names independently. Do not infer manufacturing country
from brand registration, design origin, distributor address or marketing language.

## 5. Find meaningful product features

For each series and subtype present in the store assortment, search for concrete,
buyer-relevant details such as:

- exact material grade or thickness;
- coating process and layer information;
- named cartridge, aerator, valve, fitting or mechanism manufacturer;
- closer, hinge, roller or flush mechanism design;
- pressure, flow, load, cycle, temperature or protection ratings;
- installation, maintenance and compatibility constraints;
- model-specific warranty or certification.

Reject unsupported phrases such as “premium quality,” “European standard,” “reliable”
or “innovative.” A useful differentiator must contain a named mechanism, measurable
property, verified design choice or clearly documented service condition.

Deliberately search for series where no meaningful technical distinction appears.
Report that null result instead of inventing an advantage.

## 6. Translate detail into buyer value cautiously

Use:

`verified technical detail → supported practical consequence → relevant buyer scenario`

The practical consequence must follow from the documented mechanism or from a credible
technical source. Mark a reasonable but not directly documented consequence as
`[inference]` and explain the reasoning. Never turn it into a categorical promise.

Avoid exaggerated outcomes. For example, a material grade alone does not prove that a
complete assembly will withstand a hydraulic shock; pressure-test data for the assembly
would be needed.

Include limitations and trade-offs when relevant: care requirements, installation
conditions, consumable availability, compatibility or warranty exclusions.

## 7. Test whether a difference is actually distinctive

Build a comparison set of 5–8 direct competitors:

- same product subtype;
- comparable price segment in the relevant market;
- similar configuration and installation type;
- products currently available or documented in a comparable period.

Define the compared feature precisely before counting. Check direct or official sources
for each competitor and show the denominator:

- feature found in 0–1 competitors: **strong candidate differentiator**;
- feature found in a minority but more than one: **uncommon feature**;
- feature found in at least half: **industry standard/common feature**;
- insufficient comparable evidence: **uniqueness not established**.

Do not call a feature exclusive unless exhaustive market evidence or an enforceable
exclusive right supports that word. Prefer “not found among N checked competitors.”

Compare total product value, not isolated specifications, only when configurations and
prices are genuinely comparable. Price differences above 15–20% from the comparison
median may be reported as meaningful; state date, market and sample.

## 8. Use additional verification channels with discipline

When a claim makes them relevant, check:

- patent and certification registries;
- accreditation, recall or certificate-withdrawal records;
- installer/contractor discussions;
- repeated marketplace defects;
- reverse-image search for possible rebadging;
- official versus parallel-import warranty status.

“Searched and found nothing” is not proof of absence. Record queries, identifiers and
scope. Require an exact legal entity, registration number, batch or certificate number
when the registry needs it.

Treat a defect pattern as a signal only after at least five plausibly independent,
specific mentions for the same mechanism/model family. Deduplicate reposts and copied
reviews. Reviews establish reported experience, not engineering causation.

If a channel is unavailable, mark it `not attempted` or `inconclusive`.

## 9. Quality gate

Before finalizing, verify:

- every store product/series in scope is represented or listed as unresolved;
- every factual sentence has a source;
- model-level evidence was not expanded to the brand;
- copied retailer descriptions were not counted independently;
- all numbers retain units, conditions and dates;
- competitor comparisons use a declared segment and denominator;
- “unique,” “exclusive,” “best” and durability claims meet the evidence threshold;
- technical details are translated into benefits without overstating causality;
- contradictions and access limitations remain visible;
- addresses distinguish manufacturer, representative, brand showroom and reseller;
- no empty section is padded with generic marketing.

If evidence is too weak, deliver a smaller accurate report and a concrete open-questions
list rather than a complete-looking speculative one.


