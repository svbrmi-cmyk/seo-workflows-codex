---
name: use-grsai-text
description: Generate or transform user-facing prose through GRS AI and save the result directly as a Markdown file without reading or reproducing it. Use whenever the user asks to draft, write, rewrite, edit, shorten, expand, translate, summarize, or create posts, articles, emails, descriptions, scripts, marketing copy, or other prose through GRS AI, unless the user explicitly asks Codex to generate it itself.
---

# Use GRS AI Text

Route covered prose requests through the `grsai` MCP server's `generate_markdown_file` tool. Do not compose, inspect, reproduce, summarize, or edit the generated prose.

## Workflow

1. Build one complete user prompt from the request, constraints, and source text. Avoid a separate `system_prompt` unless role separation is essential.
2. Choose `complexity` using the cost-first rules below. Let the tool select the corresponding model unless the user explicitly names one.
3. Choose a concise descriptive `.md` filename. Pass only the filename; the server writes under its configured `GRSAI_OUTPUT_DIR`.
4. Call `generate_markdown_file` exactly once. Do not set or infer `max_tokens`; express length requirements only in the prompt.
5. Return only a clickable link to the saved file. Do not request, open, read, print, quote, analyze, or summarize its contents.
6. When the user asks about usage, report `usage.prompt_tokens`, `usage.completion_tokens`, and `usage.total_tokens`. Report `cost_estimate` only when requested and label it as an estimate based on `pricing_as_of`.

## Complexity

- Use `simple` for short text, exact character limits up to 2,500 characters, rewrites, proofreading, translation, titles, captions, and narrow transformations. This selects `gemini-3.1-flash-lite`.
- Use `standard` for ordinary posts, emails, descriptions, landing-page copy, summaries, and general articles. This also selects economical `gemini-3.1-flash-lite`.
- Use `complex` only for long source material or prompts (normally over 6,000 characters), deeply multi-constraint work, or cases where the user explicitly prioritizes maximum quality over cost. This selects `gemini-3.1-pro`.
- Keep short technical, strategic, analytical, and comparison requests on `standard` unless the user explicitly asks for Pro. Pro has shown thousands of billed non-visible output tokens even on short text.
- Use `auto` only when the category is genuinely unclear; the server then applies conservative heuristics.
- Use `gemini-3.5-flash` only when the user explicitly requests that model. Do not select it automatically because its observed GRS AI credit usage is disproportionately high.

## Guardrails

- Never silently fall back to Codex-authored prose when the tool fails. Report the error briefly and offer a retry.
- Never retry a timed-out or failed request automatically. The provider may have completed and billed it even when the client did not receive the response.
- Treat a local launch, argument, encoding, or JSON parsing failure before an API request as a local failure; fix it before making the single API call.
- Reuse a cached result when the tool marks it as `cached`; this prevents duplicate charges for identical requests within 15 minutes.
- Treat `output_metrics.high_nonvisible_token_signal` as a warning that reasoning or other non-visible tokens dominate the response cost.
- Do not send unrelated workspace data, credentials, or private context to GRS AI.
- Never embed an API key in prompts, Markdown files, source code, tool output, or repository files. Reject obvious keys for another provider rather than sending them to GRS AI.
- Do not use this workflow for ordinary factual answers, analysis, code generation, or casual conversation unless the user specifically asks for generated prose.
- For revisions of GRS AI output, call the tool again and save a new Markdown file rather than opening or editing the previous result locally.
