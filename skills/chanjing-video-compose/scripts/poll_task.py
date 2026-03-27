#!/usr/bin/env python3
"""
轮询视频合成任务状态，直到完成或失败。
用法: poll_task.py --id <video_id> [--interval 10] [--json]
输出: 默认成功时打印 video_url；--json 时输出完整 data
状态: 10-生成中, 30-成功, 4X 参数异常, 5X 服务异常
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
    parser = argparse.ArgumentParser(description="轮询蝉镜视频合成任务直到完成")
    parser.add_argument("--id", required=True, help="视频任务 ID（来自 create_task）")
    parser.add_argument("--interval", type=int, default=10, help="轮询间隔秒数，默认 10")
    parser.add_argument("--json", action="store_true", help="成功后输出完整 JSON data")
    args = parser.parse_args()

    token, err = get_token()
    if err:
        print(err, file=sys.stderr)
        sys.exit(1)

    url = f"{API_BASE}/open/v1/video?id={urllib.parse.quote(args.id)}"

    while True:
        req = urllib.request.Request(url, headers={"access_token": token}, method="GET")
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))

        if body.get("code") != 0:
            print(body.get("msg", body), file=sys.stderr)
            sys.exit(1)

        data = body.get("data", {})
        status = data.get("status")

        if status == 30:
            if args.json:
                print(json.dumps(data, ensure_ascii=False, indent=2))
                return 0
            video_url = data.get("video_url")
            if video_url:
                print(video_url)
                return 0
            print("任务成功但无 video_url", file=sys.stderr)
            sys.exit(1)

        if isinstance(status, int) and status >= 40:
            err_msg = data.get("msg") or f"status={status}"
            print(f"任务失败: {err_msg}", file=sys.stderr)
            sys.exit(1)

        time.sleep(args.interval)


if __name__ == "__main__":
    main()
