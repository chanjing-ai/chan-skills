#!/usr/bin/env python3
"""
获取定制数字人详情。
用法: get_person.py --id <person_id> [--field preview_url]
默认输出: 详情 JSON
"""
import argparse
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _auth import get_token

API_BASE = (__import__("os").environ.get("CHANJING_OPENAPI_BASE_URL") or __import__("os").environ.get("CHANJING_API_BASE") or "https://open-api.chanjing.cc").rstrip("/")


def main():
    parser = argparse.ArgumentParser(description="获取定制数字人详情")
    parser.add_argument("--id", required=True, help="定制数字人 id")
    parser.add_argument("--field", help="仅输出 data 下的某个字段")
    args = parser.parse_args()

    token, err = get_token()
    if err:
        print(err, file=sys.stderr)
        sys.exit(1)

    url = f"{API_BASE}/open/v1/customised_person?id={urllib.parse.quote(args.id)}"
    req = urllib.request.Request(url, headers={"access_token": token}, method="GET")
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode("utf-8"))

    if result.get("code") != 0:
        print(result.get("msg", result), file=sys.stderr)
        sys.exit(1)

    data = result.get("data", {})
    if args.field:
        value = data.get(args.field)
        if value is None:
            print(f"字段不存在: {args.field}", file=sys.stderr)
            sys.exit(1)
        if isinstance(value, (dict, list)):
            print(json.dumps(value, ensure_ascii=False))
        else:
            print(value)
        return

    print(json.dumps(data, ensure_ascii=False))


if __name__ == "__main__":
    main()
