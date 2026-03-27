#!/usr/bin/env python3
"""
轮询定制数字人状态，直到成功或失败。
用法: poll_person.py --id <person_id> [--interval 10] [--timeout 1800] [--json]
状态: 1=制作中, 2=成功, 4=失败, 5=系统错误
"""
import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _auth import get_token

API_BASE = (__import__("os").environ.get("CHANJING_OPENAPI_BASE_URL") or __import__("os").environ.get("CHANJING_API_BASE") or "https://open-api.chanjing.cc").rstrip("/")
SUCCESS_STATUS = 2
RUNNING_STATUS = 1
FAILED_STATUSES = {4, 5}


def fetch_detail(token, person_id):
    url = f"{API_BASE}/open/v1/customised_person?id={urllib.parse.quote(person_id)}"
    req = urllib.request.Request(url, headers={"access_token": token}, method="GET")
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    if body.get("code") != 0:
        return None, body.get("msg", body)
    return body.get("data", {}), None


def main():
    parser = argparse.ArgumentParser(description="轮询定制数字人状态直到完成")
    parser.add_argument("--id", required=True, help="定制数字人 id")
    parser.add_argument("--interval", type=int, default=10, help="轮询间隔秒数，默认 10")
    parser.add_argument("--timeout", type=int, default=1800, help="轮询超时秒数，默认 1800")
    parser.add_argument("--json", action="store_true", help="成功时输出完整 JSON")
    args = parser.parse_args()

    token, err = get_token()
    if err:
        print(err, file=sys.stderr)
        sys.exit(1)

    deadline = time.monotonic() + args.timeout
    while time.monotonic() < deadline:
        data, err = fetch_detail(token, args.id)
        if err:
            print(err, file=sys.stderr)
            sys.exit(1)

        status = data.get("status")
        if status == SUCCESS_STATUS:
            if args.json:
                print(json.dumps(data, ensure_ascii=False))
                return
            preview_url = data.get("preview_url")
            print(preview_url or data.get("id", ""))
            return

        if status in FAILED_STATUSES:
            message = data.get("err_reason") or data.get("reason") or "unknown"
            print(f"任务失败: {message}", file=sys.stderr)
            sys.exit(1)

        if status != RUNNING_STATUS:
            print(f"未知状态: {status}", file=sys.stderr)
            sys.exit(1)

        time.sleep(args.interval)

    print("轮询超时", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
