#!/usr/bin/env python3
"""
轮询对口型视频任务状态，直到完成或失败。与 chanjing-credentials-guard 使用同一配置文件获取 Token。
用法: poll_task.py --id <视频任务id> [--interval 10]
输出: 成功时打印 video_url（一行），失败时打印错误到 stderr 并 exit 1
状态: 0-待处理 10-生成中 20-成功 30-失败
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
    parser = argparse.ArgumentParser(description="轮询对口型视频任务直到完成")
    parser.add_argument("--id", required=True, help="视频任务 ID（来自 create_task）")
    parser.add_argument("--interval", type=int, default=10, help="轮询间隔秒数，默认 10")
    args = parser.parse_args()

    token, err = get_token()
    if err:
        print(err, file=sys.stderr)
        sys.exit(1)

    url = f"{API_BASE}/open/v1/video_lip_sync/detail?id={urllib.parse.quote(args.id)}"

    while True:
        req = urllib.request.Request(url, headers={"access_token": token}, method="GET")
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))

        if body.get("code") != 0:
            print(body.get("msg", body), file=sys.stderr)
            sys.exit(1)

        data = body.get("data", {})
        status = data.get("status")
        progress = data.get("progress", 0)

        if status == 20:
            video_url = data.get("video_url")
            if video_url:
                print(video_url)
                return 0
            print("任务成功但无 video_url", file=sys.stderr)
            sys.exit(1)

        if status == 30:
            print(f"任务失败: {data.get('msg', 'unknown')}", file=sys.stderr)
            sys.exit(1)

        # 0 或 10：继续轮询
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
