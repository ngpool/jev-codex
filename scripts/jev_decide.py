#!/usr/bin/env python3
"""Send a typed judgment request to TypeSafe Jev and print its JSON response."""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ENDPOINT = "https://api.typesafe.ai/v1/systemone"
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
TRACE_LOG_FILE = Path(__file__).resolve().parent.parent / "jev-trace.log"


def log_trace(message: str) -> None:
    """Write trace metadata to stderr and append it to the local trace log."""
    print(message, file=sys.stderr)
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    try:
        if TRACE_LOG_FILE.exists() and TRACE_LOG_FILE.stat().st_size:
            with TRACE_LOG_FILE.open("rb") as existing_log:
                existing_log.seek(-1, os.SEEK_END)
                needs_separator = existing_log.read(1) != b"\n"
        else:
            needs_separator = False
        with TRACE_LOG_FILE.open("a", encoding="utf-8") as log_file:
            if needs_separator:
                log_file.write("\n")
            log_file.write(f"{timestamp} {message}\n")
    except OSError as exc:
        print(f"[jev trace] could not write {TRACE_LOG_FILE}: {exc}", file=sys.stderr)


def load_api_key_from_env_file() -> None:
    """Load TYPESAFE_API_KEY from the skill's optional .env file."""
    try:
        lines = ENV_FILE.read_text(encoding="utf-8-sig").splitlines()
    except FileNotFoundError:
        return

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].lstrip()

        name, separator, value = line.partition("=")
        if not separator or name.strip() != "TYPESAFE_API_KEY":
            continue

        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if not os.environ.get("TYPESAFE_API_KEY"):
            os.environ["TYPESAFE_API_KEY"] = value
        return


def main() -> int:
    parser = argparse.ArgumentParser(description="Send a typed judgment request to TypeSafe Jev.")
    parser.add_argument(
        "--trace",
        action="store_true",
        help="log request and response details to stderr and jev-trace.log (never logs the API key)",
    )
    args = parser.parse_args()

    load_api_key_from_env_file()
    api_key = os.environ.get("TYPESAFE_API_KEY")
    if not api_key:
        print("TYPESAFE_API_KEY is not set.", file=sys.stderr)
        return 2

    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON on stdin: {exc}", file=sys.stderr)
        return 2

    if not isinstance(payload, dict) or not {"model", "state", "questions"}.issubset(payload):
        print('Request must be a JSON object with "model", "state", and "questions".', file=sys.stderr)
        return 2

    request_body = json.dumps(payload).encode("utf-8")
    request = Request(
        ENDPOINT,
        data=request_body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    started_at = time.perf_counter()
    if args.trace:
        questions = payload.get("questions")
        question_count = len(questions) if isinstance(questions, dict) else "unknown"
        state = payload.get("state")
        log_trace(
            f"[jev trace] POST {ENDPOINT}; model={payload.get('model', 'unknown')}; "
            f"state_type={type(state).__name__}; questions={question_count}; "
            f"request_bytes={len(request_body)}"
        )
        log_trace(
            "[jev trace] request="
            + json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        )

    try:
        with urlopen(request, timeout=30) as response:
            result = response.read().decode("utf-8")
            status = response.status
    except HTTPError as exc:
        elapsed = time.perf_counter() - started_at
        if args.trace:
            log_trace(f"[jev trace] HTTP {exc.code}; elapsed={elapsed:.3f}s")
        detail = exc.read().decode("utf-8", errors="replace")
        if args.trace:
            log_trace(
                "[jev trace] response_error="
                + json.dumps(detail, ensure_ascii=False)
            )
        print(f"TypeSafe API returned HTTP {exc.code}: {detail}", file=sys.stderr)
        return 1
    except (URLError, TimeoutError) as exc:
        elapsed = time.perf_counter() - started_at
        if args.trace:
            log_trace(
                f"[jev trace] request failed; elapsed={elapsed:.3f}s; "
                f"error_type={type(exc).__name__}"
            )
        print(f"Could not reach TypeSafe API: {exc}", file=sys.stderr)
        return 1

    elapsed = time.perf_counter() - started_at
    try:
        parsed = json.loads(result)
    except json.JSONDecodeError:
        if args.trace:
            log_trace(
                f"[jev trace] HTTP {status}; elapsed={elapsed:.3f}s; "
                "response was not valid JSON"
            )
            log_trace("[jev trace] response_raw=" + json.dumps(result, ensure_ascii=False))
        print("TypeSafe API returned a non-JSON response.", file=sys.stderr)
        return 1

    if args.trace:
        log_trace(
            "[jev trace] response="
            + json.dumps(parsed, ensure_ascii=False, separators=(",", ":"))
        )
        usage = parsed.get("usage", {}) if isinstance(parsed, dict) else {}
        usage_summary = ""
        if isinstance(usage, dict):
            input_tokens = usage.get("input_tokens", "unknown")
            output_tokens = usage.get("output_tokens", "unknown")
            usage_summary = f"; input_tokens={input_tokens}; output_tokens={output_tokens}"
        model = parsed.get("model", "unknown") if isinstance(parsed, dict) else "unknown"
        log_trace(
            f"[jev trace] HTTP {status}; elapsed={elapsed:.3f}s; "
            f"response_model={model}{usage_summary}"
        )

    print(json.dumps(parsed, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
