#!/usr/bin/env python3
"""
轮询 AI 创作任务直到完成。
默认输出第一个结果地址；可用 --json 输出完整详情。
"""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _auth import get_token
from _task_api import FAILED_STATUSES, RUNNING_STATUSES, SUCCESS_STATUSES, first_output_url, get_task


def main():
    parser = argparse.ArgumentParser(description="轮询 AI 创作任务直到完成")
    parser.add_argument("--unique-id", required=True, help="创作任务 unique_id")
    parser.add_argument("--interval", type=int, default=10, help="轮询间隔秒数，默认 10")
    parser.add_argument("--timeout", type=int, default=1800, help="轮询超时秒数，默认 1800")
    parser.add_argument("--json", action="store_true", help="成功时输出完整 JSON")
    parser.add_argument("--all-urls", action="store_true", help="成功时输出全部 output_url JSON 数组")
    args = parser.parse_args()

    token, err = get_token()
    if err:
        print(err, file=sys.stderr)
        sys.exit(1)

    deadline = time.monotonic() + args.timeout
    while time.monotonic() < deadline:
        try:
            data = get_task(token, args.unique_id)
        except Exception as exc:
            print(str(exc), file=sys.stderr)
            sys.exit(1)

        status = data.get("progress_desc")
        if status in SUCCESS_STATUSES:
            if args.json:
                print(json.dumps(data, ensure_ascii=False))
                return
            urls = data.get("output_url") or []
            if args.all_urls:
                print(json.dumps(urls, ensure_ascii=False))
                return
            first_url = first_output_url(data)
            if not first_url:
                print("任务成功但无 output_url", file=sys.stderr)
                sys.exit(1)
            print(first_url)
            return

        if status in FAILED_STATUSES:
            print(f"任务失败: {data.get('err_msg') or status}", file=sys.stderr)
            sys.exit(1)

        if status not in RUNNING_STATUSES:
            print(f"未知任务状态: {status}", file=sys.stderr)
            sys.exit(1)

        time.sleep(args.interval)

    print("轮询超时", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
