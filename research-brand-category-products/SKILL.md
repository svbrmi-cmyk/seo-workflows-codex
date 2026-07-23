---
name: research-brand-category-products
description: Research and fact-check a brand's product categories using a supplied brand name and an online-store brand or category URL. Use when Codex must map which product categories the brand actually sells in one store, measure category breadth, find category-level features and technologies, compare categories with same-segment alternatives, distinguish genuine differentiators from industry standards, translate verified details into buyer benefits, and produce a source-tagged report without turning the result into a product-by-product catalog.
---

# Research Brand Category Products

Use `scripts/perplexity_search.py` as the primary tool for online search, source
discovery and fact-verification queries. The script calls the official Perplexity Sonar
API, reads its credential only from `PERPLEXITY_API_KEY`, and returns structured JSON
containing the answer and source records.

Run it from this skill directory:

```text
python scripts/perplexity_search.py "precise research or verification query"
```

Never treat a Perplexity conclusion about page access, page contents, absence of
documents or absence of products as final without a direct check.

Use this retrieval sequence:

1. Open the user-supplied URL directly before asking Perplexity to describe it.
2. Use Perplexity to discover official, retailer, competitor and registry sources.
3. Open relevant returned URLs directly and read them before labeling evidence
   `[direct]` or `[document]`.
4. If Perplexity returns an API error, no useful sources, an inaccessible-page claim,
   incomplete category coverage, or a conclusion contradicted by direct reading, use a
   general-purpose web search as a controlled fallback.
5. Record why fallback search was triggered and which source URLs it added. Verify
   fallback results directly under the same evidence rules.

Do not use remembered knowledge as fallback evidence. If `PERPLEXITY_API_KEY` is
missing, Python cannot run, or both Perplexity and fallback search are unavailable,
stop the affected online research and report the exact blocker. Never silently switch
providers or conceal a disagreement between Perplexity and directly read evidence.

Treat Perplexity and fallback search results as discovery records, not factual proof.
If a returned page cannot be opened, keep its evidence label `[snippet]` and do not
imply that its full contents were verified.

Accept two required inputs:

- brand name;
- online-store brand or category URL.

Treat the store page as the boundary of the assortment under study. The primary unit of
analysis is a **product category or subtype**, not an individual SKU. Use individual
products only as representative evidence for a category-level claim, price range or
technical example. Do not turn the report into a complete product catalog unless the
user explicitly requests SKU-level enumeration.

Produce the most complete category-level report the available evidence supports. Never
fill a gap with memory, inference presented as fact, or an industry-typical
characteristic.

Read [references/report-template.md](references/report-template.md) before drafting the
final result.

## 1. Establish scope and access

Open the supplied store URL directly and identify:

- store and market/region;
- category and any active filters;
- whether the page is brand-filtered;
- access date;
- displayed total product count;
- product-category tabs, filters, subcategories and their displayed counts;
- whether category navigation, lazy loading and representative product cards are
  readable directly.

If Perplexity says that the supplied page is unavailable or empty but direct access
succeeds, classify the Perplexity access claim as contradicted and continue from the
direct page. If direct access fails, trigger fallback search for the exact URL, domain,
brand and visible indexed category pages.

Check access separately for the store, official manufacturer, official regional
representative and other important sources.

Label evidence:

- `[direct]` — the page itself was opened and read;
- `[document]` — an official catalog, certificate or manual was read;
- `[snippet]` — only a search-result snippet was available;
- `[user-supplied]` — supplied by the user and not yet independently verified.

State access limitations before findings. Do not silently treat snippets as direct
evidence.

## 2. Map product categories in the store

Map only the named brand's categories and subtypes present within the supplied store
scope. Handle category tabs, filters, pagination, lazy loading and variant-heavy
listings.

Record for every category or subtype:

- exact store label;
- displayed product count and share of the brand assortment when available;
- representative series or collections;
- representative product types or configurations;
- observed price range and availability pattern;
- category/filter URL when available;
- two to five representative SKU examples only when they help substantiate category
  breadth, features or price.

Do not enumerate every product by default. Use enough representative products to
validate the category findings. Deduplicate representative examples by SKU/article
first, then canonical URL, then exact model identity.

Report:

- the store's displayed total product count;
- the sum of displayed category counts;
- whether categories overlap;
- the number of categories and subtypes independently mapped;
- the number of representative products checked.

If category counts do not reconcile with the total, determine whether tabs overlap,
variants are counted separately, or lazy loading hides categories. Treat a large gap
between total products and visible cards as a coverage limitation, not automatically
as catalog inconsistency.

Use the category map to define research priorities: cover every category found and
investigate the most represented or technically diverse categories first. Never
research unrelated brand categories unless needed for context and clearly marked out
of scope.

## 3. Build the source map

Find and distinguish:

1. official manufacturer site;
2. official site for the relevant country or regional representative;
3. official catalogs, manuals, certificates and product data sheets;
4. the supplied store's brand, category and representative product pages;
5. two or more established specialist retailers carrying the same categories;
6. same-category competitor sources needed to test differentiation;
7. registries, installer sources and review datasets when relevant.

Use the official source for brand history, production geography, named technologies,
series architecture and certifications. Use store and retailer cards to confirm what is
actually sold locally, not to establish unsupported corporate claims.

Before treating sources as independent confirmations, compare their wording. Identical
or near-identical descriptions copied from one supplier feed count as one evidence
chain. Record the likely common origin.

Prefer official category, collection, technology and document pages for category-level
claims. Use exact product/model pages only to prove representative examples. Record
publication/update date when available and always record access date.

## 4. Atomize and verify claims

Convert every candidate statement into one atomic, checkable claim. Separate combined
sentences into:

- identity claims: brand, manufacturer, legal entity;
- dates and geography;
- product-category, subtype, series and representative SKU names;
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

For each product category and important subtype present in the store assortment, search
for concrete, buyer-relevant details such as:

- exact material grade or thickness;
- coating process and layer information;
- named cartridge, aerator, valve, fitting or mechanism manufacturer;
- closer, hinge, roller or flush mechanism design;
- pressure, flow, load, cycle, temperature or protection ratings;
- installation, maintenance and compatibility constraints;
- category-wide or clearly scoped warranty and certification;
- representative model evidence that illustrates, but does not automatically define,
  the whole category.

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

## 7. Test whether a category difference is actually distinctive

For each priority category, build a comparison set of 5–8 direct competing brands or
category assortments:

- same category and important subtype;
- comparable price segment in the relevant market;
- similar range of configurations and installation types;
- assortments currently available or documented in a comparable period.

Define the compared feature precisely before counting. Check direct or official sources
for each competitor and show the denominator:

- feature found in 0–1 competitors: **strong candidate differentiator**;
- feature found in a minority but more than one: **uncommon feature**;
- feature found in at least half: **industry standard/common feature**;
- insufficient comparable evidence: **uniqueness not established**.

Do not call a feature exclusive unless exhaustive market evidence or an enforceable
exclusive right supports that word. Prefer “not found among N checked competitors.”

Compare category coverage, feature availability, documented technology and price bands.
Use individual products only as representative comparison points. Price differences
above 15–20% from the comparison median may be reported as meaningful; state date,
market and sample.

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

- every store product category in scope is represented or listed as unresolved;
- the report is organized by categories rather than as a product-by-product catalog;
- representative SKUs are not presented as the entire assortment;
- every factual sentence has a source;
- model-level evidence was not expanded to the brand;
- model-level evidence was not expanded to a category without explicit support;
- copied retailer descriptions were not counted independently;
- all numbers retain units, conditions and dates;
- competitor comparisons use a declared segment and denominator;
- “unique,” “exclusive,” “best” and durability claims meet the evidence threshold;
- technical details are translated into benefits without overstating causality;
- contradictions and access limitations remain visible;
- Perplexity access and absence claims were checked directly;
- fallback search triggers and added sources are disclosed;
- addresses distinguish manufacturer, representative, brand showroom and reseller;
- no empty section is padded with generic marketing.

If evidence is too weak, deliver a smaller accurate report and a concrete open-questions
list rather than a complete-looking speculative one.

