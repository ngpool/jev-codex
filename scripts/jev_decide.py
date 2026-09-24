#!/usr/bin/env python3
"""Send a typed judgment request to TypeSafe Jev and print its JSON response."""

import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ENDPOINT = "https://api.typesafe.ai/v1/systemone"
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


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

    request = Request(
        ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=30) as response:
            result = response.read().decode("utf-8")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        print(f"TypeSafe API returned HTTP {exc.code}: {detail}", file=sys.stderr)
        return 1
    except (URLError, TimeoutError) as exc:
        print(f"Could not reach TypeSafe API: {exc}", file=sys.stderr)
        return 1

    try:
        parsed = json.loads(result)
    except json.JSONDecodeError:
        print("TypeSafe API returned a non-JSON response.", file=sys.stderr)
        return 1

    print(json.dumps(parsed, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
