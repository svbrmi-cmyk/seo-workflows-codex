---
name: brand-differentiation-audit
description: 'Given only a brand name, researches and fact-checks that brand''s actual product differences, features, and advantages — separating genuine, rare differentiators from industry-standard features restated as marketing, and separating confirmed facts from unconfirmed or contradicted ones. Trigger on requests to find отличия/особенности/преимущества товаров бренда, fact-check brand/catalog claims, verify product specs against sources, or build a competitive differentiation table for a specific brand. Companion to brand-dna-summary: that skill profiles a whole company from its website; this skill does line-by-line fact verification of a single brand''s product claims against a source hierarchy. Do NOT use for a general company overview with no specific brand/product claims to verify — use brand-dna-summary for that.'
metadata:
  category: strategy-and-discovery
  source: 'Built from a user-supplied fact-checking methodology, hardened against gaps found in review: no explicit degraded-access protocol, ''standard vs unique'' judged by model memory instead of a count, no dedup check for copy-pasted ''independent'' sources, no significance threshold for numeric discrepancies, no direct/snippet or date-of-access tagging in the output table.'
---

# Brand Differentiation Audit

Input: a brand name (and optionally category scope, e.g. "унитазы", or raw text/claims
already collected by the user). Output: a fact-checked, source-tagged picture of what
that brand's products actually differ in — with genuine differentiators clearly
separated from industry-standard features being marketed as if unique, and with every
claim classified as confirmed, contradicted, or unverifiable. Never pad a gap with a
plausible-sounding industry-standard guess.

---

## Phase 0: Confirm access before claiming anything

Before researching, establish whether you can actually read target pages directly
(brand's official site, official distributor, retailer product cards) or whether access
is restricted (network policy block, JS-heavy page, paywall — check explicitly, don't
assume a fetch failure is transient).

- If direct read works: tag every fact `[direct]` in the output.
- If it doesn't: tag every fact `[snippet]` and say so in the first line of the
  response, before any findings. The entire method rests on "verify from the actual page,
  not from memory" — if this is silently violated at the start, everything downstream is
  theater. A snippet-derived brief is real, useful information, but it is categorically
  weaker (fewer exact quotes, no verified page-load-time content, missed detail pages),
  and the person needs to know which one they're getting.

## Phase 1: Map the brand's catalog from scratch

If starting from just a brand name (no pre-supplied category counts), establish
structure before hunting for differences:

1. Find the brand's official manufacturer site.
2. Find the official regional distributor/representative, separately from the
   manufacturer — establish whether local stock is direct-import or parallel import
   (this affects how much to trust localized specs and warranty claims).
3. Find 2-3 major category retailers carrying the brand with full product cards (not
   just a passing mention).
4. Collect the catalog structure: product categories + item counts per category, pulled
   from actual catalog/filter pages, not from marketing copy.
5. Prioritize categories with the most SKUs and the most series/line diversity for deep
   research — that's where engineering differences show up; categories with few SKUs
   tend to be pure marketing copy with nothing to verify.

If the user already supplied category counts/claims, skip straight to Phase 2 using
their numbers as the atomic claims to check.

## Phase 2: Atomize claims

Break any supplied text (or, if starting from a bare brand name, your own research
questions per category from Phase 1) into atomic checkable units: counts (models,
brands, employees), facts (country of origin, founding year), names (series, SKUs),
technical specs (glass thickness, cartridge type, standards).

## Phase 3: Source hierarchy — with a duplication check

Trust order:
1. Official brand/manufacturer site (catalog page, "About the brand", product cards)
2. Official regional distributor site — for claims about the brand itself, not a
   specific reseller
3. Major category retailers with full product cards — for cross-checking models,
   SKUs, country of origin
4. Niche review articles — supplementary only, never the sole source for a claim

**Before counting a second source as independent confirmation, check it against the
first for near-verbatim text overlap.** Identical copy across three retail sites is one
copied supplier feed, not three sources. Only count it as independent corroboration if
it's phrased differently or adds a detail/number the first source doesn't have.

## Phase 4: Hunt for differences, in-line and cross-market

For each priority category from Phase 1:

1. Use targeted queries: `[brand] + category + the specific part that usually breaks or
   raises a buying question` (cartridge, glass thickness, closer type, roller material),
   not generic "advantages of [brand]" queries.
2. Look for differences **between series within the brand**, not only brand-vs-brand —
   this is where real engineering detail lives (e.g. a distributor post covering
   materials/mechanisms across 4 series at once beats any generic brand description).
3. Discard marketing language with no number, standard, or mechanism name ("premium
   quality", "European standards") — not evidence.
4. Deliberately search categories where no difference is likely to turn up, and report
   that explicitly as a finding — the absence of a differentiator after a real search is
   as informative as finding one, and must not be silently dropped or papered over with a
   generic claim.

## Phase 5: Classify "genuinely unique" vs "industry standard" — by count, not impression

This is the load-bearing correction to the source methodology: don't decide "this is
already commonplace in the category" from general impression/memory — that itself is an
unverified claim, and it's the one place the method usually quietly breaks its own "not
from memory" rule.

- For every candidate differentiator, explicitly check how many of 5-8 direct
  competitors in the same price segment have the same feature/technology.
- If most do (e.g. 4 of 6): label it **industry standard**, and name which competitors
  also have it.
- If it's rare (0-1 of 6): label it **genuine differentiator**.
- This turns a subjective call into a re-checkable fact.

## Phase 6: Additional verification channels — with null-result discipline

Use these, but always distinguish "searched and found nothing" from "confirmed absent":

| Channel | What it gives | Discipline required |
|---|---|---|
| Patent/certification registries (Rospatent, Espacenet) | Whether a "proprietary" named technology is actually patented, vs. a marketing name for a standard solution | Tag `not found — searched N phrasings`, distinct from `confirmed absent` |
| Trade/installer forums (santechniki.com-type, contractor forums) | Real engineering reputation of a part/mechanism — stronger signal than marketing copy | — |
| Price benchmarking across 2-3 marketplaces | A "premium" claim contradicted by below-median pricing for the same materials is a real signal | Flag as significant only above a threshold — e.g. >15-20% below category median |
| Recall/certification-withdrawal registries (e.g. Росаккредитация) | Confirms or surfaces a systemic quality issue the marketing doesn't mention | Requires exact legal-entity/INN or batch number for a real check — a keyword search returning nothing is `search inconclusive`, not `confirmed no recalls` |
| Reverse image search on product photos | Surfaces white-label/rebadged manufacturing (common in plumbing/hardware) | Only if an image-search capability is actually available — if not, mark as not attempted, don't silently skip and imply it was checked |
| Defect-frequency aggregation across marketplace reviews | A repeated specific complaint (5+ independent mentions) outweighs one-off praise and can directly contradict a "durable mechanism" claim | Set the 5+ threshold explicitly before counting it as signal |
| Official distributor vs. parallel/grey import | Affects how much the reseller's warranty claims can be trusted | — |
| Source publish date | Specs change between model years; an old article can describe a superseded version | On conflict, prefer the newer source, but state both dates rather than silently picking one |

## Phase 7: Numeric cross-validation with a significance threshold

Cross-check any supplied or claimed counts (e.g. "sum across categories should equal
472 models") against actual catalog/filter-page counters. Treat discrepancies under
~3% as catalog noise (discontinued SKUs, items double-listed across categories);
anything larger is a red flag requiring a manual recount and an explicit note on why the
numbers diverge, not a silent reconciliation.

## Phase 8: Classify every finding into exactly three buckets

- **Confirmed by source** — name which one, plus `[direct]`/`[snippet]` and access date.
- **Directly contradicts a source** — with the exact conflicting quotes from both sides.
- **Cannot be confirmed or denied from available data** — say so plainly. Never
  substitute a plausible industry-typical guess here, even when it's likely correct.

Within "confirmed," further sort by strength using the Phase 5 count: **genuine
differentiator** vs. **industry standard** — don't present them with equal weight.

## Phase 9: Output format

1. **Findings table**: `claim | status | source | direct/snippet | access date | strength (genuine/standard)`.
2. **Ready-to-use rewritten phrasing** for every "contradicts source" finding, matching
   the original text's style, so it can be dropped in directly — don't just flag the
   error, hand over the fix.
3. A distinct **"Searched, found nothing"** section — never buried inside prose or
   silently omitted.
4. **Open questions** — what needs manual/structured follow-up (a registry lookup that
   needs an exact INN, an image for reverse search, a form only a human can submit) —
   never a vague "data may be incomplete."

Use the template at [`references/differentiation-audit-template.md`](references/differentiation-audit-template.md).
