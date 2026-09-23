#!/usr/bin/env python3
"""Send a typed judgment request to TypeSafe Jev and print its JSON response."""

import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ENDPOINT = "https://api.typesafe.ai/v1/systemone"


def main() -> int:
    api_key = os.environ.get("TYPESAFE_API_KEY")
    if not api_key:
        print("TYPESAFE_API_KEY is not set.", file=sys.stderr)
        return 2

    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON on stdin: {exc}", file=sys.stderr)
        return 2

    if not isinstance(payload, dict) or "state" not in payload or "questions" not in payload:
        print('Request must be a JSON object with "state" and "questions".', file=sys.stderr)
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
