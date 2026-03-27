#!/usr/bin/env python3
"""
轮询图生视频任务直到完成。
默认输出第一个视频地址；可用 --json 输出完整详情。
"""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _auth import get_token
from _task_api import MOTION_FAILED, MOTION_RUNNING, MOTION_SUCCESS, first_output_url, get_motion_task


def main():
    parser = argparse.ArgumentParser(description="轮询图生视频任务直到完成")
    parser.add_argument("--unique-id", required=True, help="图生视频任务 unique_id")
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
            data = get_motion_task(token, args.unique_id)
        except Exception as exc:
            print(str(exc), file=sys.stderr)
            sys.exit(1)

        status = data.get("progress_desc")
        if status in MOTION_SUCCESS:
            if args.json:
                print(json.dumps(data, ensure_ascii=False))
                return
            first_url = first_output_url(data)
            if not first_url:
                print("任务成功但无 output_url", file=sys.stderr)
                sys.exit(1)
            print(first_url)
            return

        if status in MOTION_FAILED:
            print(f"任务失败: {data.get('err_msg') or status}", file=sys.stderr)
            sys.exit(1)

        if status not in MOTION_RUNNING:
            print(f"未知任务状态: {status}", file=sys.stderr)
            sys.exit(1)

        time.sleep(args.interval)

    print("轮询超时", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
