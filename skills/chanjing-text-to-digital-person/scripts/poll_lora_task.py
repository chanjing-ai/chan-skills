#!/usr/bin/env python3
"""
轮询 LoRA 任务直到完成。
默认输出第一条 photo_task_id；可用 --json 输出完整详情。
"""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _auth import get_token
from _task_api import LORA_FAILED, LORA_RUNNING, LORA_SUCCESS, get_lora_task


def main():
    parser = argparse.ArgumentParser(description="轮询 LoRA 任务直到完成")
    parser.add_argument("--lora-id", required=True, help="LoRA 任务 ID")
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
        try:
            data = get_lora_task(token, args.lora_id)
        except Exception as exc:
            print(str(exc), file=sys.stderr)
            sys.exit(1)

        status = data.get("status")
        if status in LORA_SUCCESS:
            if args.json:
                print(json.dumps(data, ensure_ascii=False))
                return
            photo_task_ids = data.get("photo_task_ids") or []
            if not photo_task_ids:
                print("任务成功但无 photo_task_ids", file=sys.stderr)
                sys.exit(1)
            print(photo_task_ids[0])
            return

        if status in LORA_FAILED:
            print(f"任务失败: {data.get('err_msg') or status}", file=sys.stderr)
            sys.exit(1)

        if status not in LORA_RUNNING:
            print(f"未知任务状态: {status}", file=sys.stderr)
            sys.exit(1)

        time.sleep(args.interval)

    print("轮询超时", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
