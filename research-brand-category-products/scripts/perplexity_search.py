#!/usr/bin/env python3
"""Run a web-grounded Perplexity Sonar query and emit structured JSON."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any


API_URL = "https://api.perplexity.ai/v1/sonar"
DEFAULT_MODEL = "sonar-pro"
DEFAULT_SYSTEM_PROMPT = (
    "Research the request using web search. Prefer primary and official sources. "
    "Distinguish verified facts from inference, preserve dates and units, and cite "
    "sources using numbered references that correspond to the returned search results."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Query Perplexity Sonar and return the answer and sources as JSON."
    )
    parser.add_argument("query", help="Research or verification query.")
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Perplexity Sonar model (default: {DEFAULT_MODEL}).",
    )
    parser.add_argument(
        "--system",
        default=DEFAULT_SYSTEM_PROMPT,
        help="System instruction sent with the query.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=120.0,
        help="HTTP timeout in seconds (default: 120).",
    )
    return parser.parse_args()


def error_payload(kind: str, message: str, **details: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {"ok": False, "error": {"type": kind, "message": message}}
    payload["error"].update(details)
    return payload


def normalize_sources(response: dict[str, Any]) -> list[dict[str, Any]]:
    sources: list[dict[str, Any]] = []
    seen_urls: set[str] = set()

    for result in response.get("search_results") or []:
        if not isinstance(result, dict):
            continue
        url = result.get("url")
        if not isinstance(url, str) or not url or url in seen_urls:
            continue
        seen_urls.add(url)
        sources.append(
            {
                "title": result.get("title"),
                "url": url,
                "date": result.get("date"),
                "last_updated": result.get("last_updated"),
                "snippet": result.get("snippet"),
                "source": result.get("source"),
            }
        )

    # Preserve citation URLs if an API response omits search_results.
    for url in response.get("citations") or []:
        if isinstance(url, str) and url and url not in seen_urls:
            seen_urls.add(url)
            sources.append(
                {
                    "title": None,
                    "url": url,
                    "date": None,
                    "last_updated": None,
                    "snippet": None,
                    "source": "citation",
                }
            )
    return sources


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    args = parse_args()
    api_key = os.environ.get("PERPLEXITY_API_KEY")
    if not api_key:
        print(
            json.dumps(
                error_payload(
                    "missing_api_key",
                    "PERPLEXITY_API_KEY is not set; no fallback search was attempted.",
                ),
                ensure_ascii=False,
                indent=2,
            ),
            file=sys.stderr,
        )
        return 2

    request_body = {
        "model": args.model,
        "messages": [
            {"role": "system", "content": args.system},
            {"role": "user", "content": args.query},
        ],
    }
    request = urllib.request.Request(
        API_URL,
        data=json.dumps(request_body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "research-brand-category-products/1.0",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=args.timeout) as response:
            raw_response = response.read().decode("utf-8")
        api_response = json.loads(raw_response)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            api_error: Any = json.loads(body)
        except json.JSONDecodeError:
            api_error = body
        print(
            json.dumps(
                error_payload(
                    "http_error",
                    f"Perplexity API returned HTTP {exc.code}.",
                    status=exc.code,
                    response=api_error,
                ),
                ensure_ascii=False,
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1
    except (urllib.error.URLError, TimeoutError) as exc:
        print(
            json.dumps(
                error_payload("network_error", str(exc)),
                ensure_ascii=False,
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1
    except json.JSONDecodeError as exc:
        print(
            json.dumps(
                error_payload("invalid_json", f"Invalid API response: {exc}"),
                ensure_ascii=False,
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1

    choices = api_response.get("choices") or []
    answer = None
    if choices and isinstance(choices[0], dict):
        message = choices[0].get("message") or {}
        if isinstance(message, dict):
            answer = message.get("content")

    output = {
        "ok": True,
        "query": args.query,
        "answer": answer,
        "sources": normalize_sources(api_response),
        "meta": {
            "id": api_response.get("id"),
            "model": api_response.get("model"),
            "created": api_response.get("created"),
            "usage": api_response.get("usage"),
        },
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
