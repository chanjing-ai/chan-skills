#!/usr/bin/env python3
"""
轮询 TTS 任务状态，直到完成或失败。与 chanjing-credentials-guard 使用同一配置文件获取 Token。
用法: poll_task.py --task-id <task_id> [--interval 3]
输出: 成功时打印音频下载 URL（data.full.url），失败时打印错误到 stderr 并 exit 1
状态: 1-生成中 9-完成
"""
import argparse
import json
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _auth import get_token

API_BASE = (__import__("os").environ.get("CHANJING_OPENAPI_BASE_URL") or __import__("os").environ.get("CHANJING_API_BASE") or "https://open-api.chanjing.cc").rstrip("/")


def main():
    parser = argparse.ArgumentParser(description="轮询 TTS 任务直到完成")
    parser.add_argument("--task-id", required=True, help="任务 ID（来自 create_task）")
    parser.add_argument("--interval", type=int, default=3, help="轮询间隔秒数，默认 3")
    args = parser.parse_args()

    token, err = get_token()
    if err:
        print(err, file=sys.stderr)
        sys.exit(1)

    url = f"{API_BASE}/open/v1/audio_task_state"
    body = json.dumps({"task_id": args.task_id}).encode("utf-8")

    while True:
        req = urllib.request.Request(
            url,
            data=body,
            headers={"access_token": token, "Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            res = json.loads(resp.read().decode("utf-8"))

        if res.get("code") != 0:
            print(res.get("msg", res), file=sys.stderr)
            sys.exit(1)

        data = res.get("data", {})
        status = data.get("status")

        if status == 9:
            full = data.get("full") or {}
            audio_url = full.get("url")
            if audio_url:
                print(audio_url)
                return 0
            print("任务完成但无 full.url", file=sys.stderr)
            sys.exit(1)

        if status not in (1, None):
            err_msg = data.get("errMsg") or data.get("errReason") or f"status={status}"
            print(f"任务失败: {err_msg}", file=sys.stderr)
            sys.exit(1)

        time.sleep(args.interval)


if __name__ == "__main__":
    main()
