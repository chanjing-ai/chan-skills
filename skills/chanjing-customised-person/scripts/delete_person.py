#!/usr/bin/env python3
"""
删除定制数字人。
用法: delete_person.py --id <person_id>
输出: 被删除的 person_id
"""
import argparse
import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _auth import get_token

API_BASE = (__import__("os").environ.get("CHANJING_OPENAPI_BASE_URL") or __import__("os").environ.get("CHANJING_API_BASE") or "https://open-api.chanjing.cc").rstrip("/")


def main():
    parser = argparse.ArgumentParser(description="删除定制数字人")
    parser.add_argument("--id", required=True, help="定制数字人 id")
    args = parser.parse_args()

    token, err = get_token()
    if err:
        print(err, file=sys.stderr)
        sys.exit(1)

    req = urllib.request.Request(
        f"{API_BASE}/open/v1/delete_customised_person",
        data=json.dumps({"id": args.id}).encode("utf-8"),
        headers={"access_token": token, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode("utf-8"))

    if result.get("code") != 0:
        print(result.get("msg", result), file=sys.stderr)
        sys.exit(1)

    print(args.id)


if __name__ == "__main__":
    main()
