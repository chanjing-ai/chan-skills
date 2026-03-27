#!/usr/bin/env python3
"""
轮询定制声音任务状态，直到完成或失败。status: 0-排队 1-进行中 2-完成 3-过期 4-失败 99-已删除
用法: poll_voice.py --voice-id <voice_id> [--interval 15]
输出: 成功时打印 voice_id（与输入一致），失败时打印错误到 stderr 并 exit 1
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


def main():
    parser = argparse.ArgumentParser(description="轮询定制声音直到就绪")
    parser.add_argument("--voice-id", required=True, help="定制声音 ID（来自 create_voice）")
    parser.add_argument("--interval", type=int, default=15, help="轮询间隔秒数，默认 15")
    args = parser.parse_args()

    token, err = get_token()
    if err:
        print(err, file=sys.stderr)
        sys.exit(1)

    url = f"{API_BASE}/open/v1/customised_audio?id={urllib.parse.quote(args.voice_id)}"

    while True:
        req = urllib.request.Request(url, headers={"access_token": token}, method="GET")
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))

        if body.get("code") != 0:
            print(body.get("msg", body), file=sys.stderr)
            sys.exit(1)

        data = body.get("data", {})
        status = data.get("status")

        if status == 2:
            print(args.voice_id)
            return 0

        if status in (3, 4, 99):
            err_msg = data.get("err_msg") or data.get("errReason") or f"status={status}"
            print(f"声音任务失败: {err_msg}", file=sys.stderr)
            sys.exit(1)

        time.sleep(args.interval)


if __name__ == "__main__":
    main()
