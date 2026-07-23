---
name: edit-seo-text-by-analysis
description: Edit Russian SEO and commercial texts from an original text, XLSX word-frequency analysis, a semantic-width word list, and an irrelevant exact-word-form report. Use when Codex must preserve meaning and facts, improve style and technical wording, add or reduce word groups to targets or medians, keep flagged exact forms within limits, and deliver a validated edited text.
---

# Edit SEO Text by Analysis

## Workflow

1. Identify the source text and every analysis artifact supplied by the user.
2. Read text files with their actual encoding. If console output is mojibake, fix output encoding or decode the bytes before interpreting words.
3. Extract XLSX rows with `scripts/extract-xlsx-analysis.ps1` when a spreadsheet reader is unavailable.
4. Build three separate requirement sets:
   - grouped word counts and their targets;
   - semantic-width words that may be added when relevant;
   - exact irrelevant word forms and their maximum allowed occurrences.
5. Edit the complete text, preserving its subject, facts, comparisons, structure, commercial intent, and conclusions.
6. Improve grammar, rhythm, terminology, headings, transitions, punctuation, and technical precision.
7. Validate the final text deterministically. Revise toward the requested limits only while every occurrence remains meaningful, accurate, grammatical, and natural.
8. Save the result as a new UTF-8 text file unless the user explicitly asks to overwrite the source.

## Interpret analysis tables

- Treat `Слово` as the word-group label and `Словоформы` as the exact members counted in that group.
- For a median table, use `Повторы` as the current count and `Медиана` as the target. Use `Добавить/Удалить` as a cross-check.
- For a range table, use `Минимум по рекомендациям` and `Максимум по рекомендациям`. If the user asks for the median, prefer the median table over the range.
- A positive adjustment means add occurrences; a negative adjustment means remove occurrences.
- Distinguish total-document recommendations from recommendations limited to text or anchor tags. Do not combine columns with different scopes.
- Treat target frequencies and medians as diagnostic reference points, not as quotas that override meaning or language quality.
- When tables conflict, follow the scope explicitly requested by the user and report a material unresolved conflict.

## Edit safely

- Preserve every substantive claim from the source unless correcting an evident language or terminology error.
- Do not invent product properties, certifications, dimensions, warranty terms, prices, availability, or comparisons to satisfy keywords.
- Insert every added word only where it accurately describes the subject of that sentence and logically develops the surrounding paragraph.
- Distribute relevant terms across the text by topic: category terms in category sections, materials and finishes in material sections, and commercial terms in purchase sections.
- Keep additions even across suitable sections when the text supports them. Do not cluster repeated exact forms in one sentence, adjacent sentences, headings, or lists merely to reach a target.
- Make every inserted form agree grammatically with its phrase and fit the sentence's syntax, terminology, register, and factual scope.
- Add semantic-width words only where the existing content supports them. Prefer category lists, navigation sentences, headings, and purchase-condition blocks.
- Do not add all width words mechanically. Skip unrelated brand names, policy terms, interface labels, and product categories that the text does not support.
- Replace excess repeated terms with accurate pronouns, hypernyms, or context-specific equivalents.
- Avoid awkward keyword insertions, fragments, tautology, promotional clichés, and unsupported superlatives.
- Accept a justified shortfall from a median when another occurrence would be repetitive, misleading, structurally misplaced, or unnatural. Record the reason briefly instead of forcing the word into the text.
- Preserve qualifications such as `по данным производителя` for manufacturer-supplied performance claims.
- Keep standards and technical terms precise. For example, describe IP ratings without implying protection beyond the stated class.

## Handle irrelevant words

- Treat the irrelevant-word report as exact-form matching, not stemming.
- If the user specifies `не больше одного раза`, leave zero or one occurrence of each flagged exact form.
- Do not remove a unique occurrence solely because it appears in the report when the allowed maximum is one and the sentence needs it.

## Validate

- Count grouped terms from the exact word forms listed in the XLSX file, case-insensitively and at word boundaries.
- Count irrelevant words by exact word form, also at word boundaries.
- Check headings because analysis services commonly count them as part of the document.
- Re-read the complete result without looking at the target table and assess it as ordinary prose. Rewrite or remove any occurrence that feels inserted for the analyzer, even if the count then falls below the median.
- Check that repeated terms are separated naturally and appear only in sections where their meaning belongs.
- Grammatical quality, logical flow, factual coherence, precision, and natural wording take priority over blindly forcing a target.
- Report the saved file and briefly state which constraints were verified. Do not overwhelm the user with internal calculations unless requested.

## Helper script

Run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/extract-xlsx-analysis.ps1 -Path analysis.xlsx
```

The script prints all populated worksheet rows as tab-separated `cell=value` fields. Use it only for extraction; interpret column scope according to the rules above.
