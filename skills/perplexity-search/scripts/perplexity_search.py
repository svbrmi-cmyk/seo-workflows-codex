#!/usr/bin/env python3
"""Search the web with Perplexity Sonar API and emit Markdown or JSON."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


DEFAULT_ENDPOINT = "https://api.perplexity.ai/v1/sonar"
DEFAULT_SYSTEM = (
    "Проведи актуальный веб-поиск. Отделяй установленные факты от выводов, "
    "не выдумывай сведения и опирайся на первичные источники. "
    "Для существенных утверждений используй ссылки из результатов поиска."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Выполнить поиск через Perplexity Sonar API."
    )
    parser.add_argument("query", nargs="?", help="Исследовательский запрос")
    parser.add_argument("--model", default="sonar-pro", help="Модель Sonar")
    parser.add_argument("--system", default=DEFAULT_SYSTEM, help="Системная инструкция")
    parser.add_argument(
        "--domain",
        action="append",
        default=[],
        help="Разрешённый домен; можно повторять (до 20)",
    )
    parser.add_argument(
        "--exclude-domain",
        action="append",
        default=[],
        help="Исключённый домен; можно повторять (до 20 вместе с --domain)",
    )
    parser.add_argument("--language", help="Язык поиска ISO 639-1, например ru")
    parser.add_argument(
        "--recency",
        choices=("hour", "day", "week", "month", "year"),
        help="Ограничение по давности публикации",
    )
    parser.add_argument("--after", help="Публикации после даты MM/DD/YYYY")
    parser.add_argument("--before", help="Публикации до даты MM/DD/YYYY")
    parser.add_argument(
        "--context-size",
        choices=("low", "medium", "high"),
        default="high",
        help="Размер поискового контекста",
    )
    parser.add_argument("--max-tokens", type=int, help="Максимум токенов ответа")
    parser.add_argument(
        "--format", choices=("markdown", "json"), default="markdown"
    )
    parser.add_argument("--output", type=Path, help="Сохранить результат в файл")
    parser.add_argument("--timeout", type=float, default=180.0, help="Таймаут, секунд")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if not args.query:
        parser.error("query is required")
    if len(args.domain) + len(args.exclude_domain) > 20:
        parser.error("Perplexity supports at most 20 domain filters")
    if args.max_tokens is not None and args.max_tokens < 1:
        parser.error("--max-tokens must be positive")
    return args


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": args.model,
        "messages": [
            {"role": "system", "content": args.system},
            {"role": "user", "content": args.query},
        ],
        "search_context_size": args.context_size,
        "language_preference": "ru",
    }
    filters = list(args.domain) + [f"-{item}" for item in args.exclude_domain]
    if filters:
        payload["search_domain_filter"] = filters
    if args.language:
        payload["search_language_filter"] = [args.language]
    if args.recency:
        payload["search_recency_filter"] = args.recency
    if args.after:
        payload["search_after_date_filter"] = args.after
    if args.before:
        payload["search_before_date_filter"] = args.before
    if args.max_tokens is not None:
        payload["max_tokens"] = args.max_tokens
    return payload


def request_search(args: argparse.Namespace, api_key: str) -> dict[str, Any]:
    request = urllib.request.Request(
        args.endpoint,
        data=json.dumps(build_payload(args), ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "codex-perplexity-search/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=args.timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        body = body.replace(api_key, "[REDACTED]")
        raise RuntimeError(f"Perplexity HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Perplexity network error: {exc.reason}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError("Perplexity returned invalid JSON") from exc


def normalize(data: dict[str, Any], query: str) -> dict[str, Any]:
    choices = data.get("choices") or []
    answer = ""
    if choices and isinstance(choices[0], dict):
        message = choices[0].get("message") or {}
        answer = message.get("content") or ""
    return {
        "query": query,
        "answer": answer,
        "citations": data.get("citations") or [],
        "search_results": data.get("search_results") or [],
        "model": data.get("model"),
        "usage": data.get("usage") or {},
    }


def markdown(result: dict[str, Any]) -> str:
    lines = [f"# Результат поиска Perplexity", "", f"**Запрос:** {result['query']}", ""]
    lines.extend(["## Ответ", "", result["answer"] or "Ответ отсутствует.", ""])
    lines.extend(["## Источники", ""])
    citations = result["citations"]
    if citations:
        lines.extend(f"{index}. <{url}>" for index, url in enumerate(citations, 1))
    else:
        lines.append("Источники не возвращены.")
    lines.extend(["", "## Поисковые результаты", ""])
    search_results = result["search_results"]
    if search_results:
        for index, item in enumerate(search_results, 1):
            title = item.get("title") or item.get("url") or f"Источник {index}"
            url = item.get("url") or ""
            date = item.get("date") or item.get("last_updated") or ""
            snippet = (item.get("snippet") or "").strip()
            suffix = f" — {date}" if date else ""
            lines.append(f"{index}. [{title}]({url}){suffix}" if url else f"{index}. {title}{suffix}")
            if snippet:
                lines.append(f"   {snippet}")
    else:
        lines.append("Поисковые результаты не возвращены.")
    lines.extend(["", f"**Модель:** {result['model'] or 'не указана'}", ""])
    return "\n".join(lines)


def write_output(content: str, output: Path | None) -> None:
    if output is None:
        sys.stdout.buffer.write(content.encode("utf-8"))
        if not content.endswith("\n"):
            sys.stdout.buffer.write(b"\n")
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")


def main() -> int:
    args = parse_args()
    api_key = os.environ.get("PERPLEXITY_API_KEY")
    if not api_key:
        print("PERPLEXITY_API_KEY is not set", file=sys.stderr)
        return 2
    try:
        result = normalize(request_search(args, api_key), args.query)
        content = (
            json.dumps(result, ensure_ascii=False, indent=2)
            if args.format == "json"
            else markdown(result)
        )
        write_output(content, args.output)
        if not result["answer"]:
            print("Warning: Perplexity returned an empty answer", file=sys.stderr)
            return 3
        return 0
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
