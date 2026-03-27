#!/usr/bin/env python3
"""
获取图生视频任务详情。
用法: get_motion_task.py --unique-id <id> [--field progress_desc] [--first-output]
默认输出: 完整 JSON
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _auth import get_token
from _task_api import first_output_url, get_motion_task


def main():
    parser = argparse.ArgumentParser(description="获取图生视频任务详情")
    parser.add_argument("--unique-id", required=True, help="图生视频任务 unique_id")
    parser.add_argument("--field", help="只输出某个字段")
    parser.add_argument("--first-output", action="store_true", help="只输出第一个输出地址")
    args = parser.parse_args()

    token, err = get_token()
    if err:
        print(err, file=sys.stderr)
        sys.exit(1)

    try:
        data = get_motion_task(token, args.unique_id)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

    if args.first_output:
        value = first_output_url(data)
        if not value:
            print("当前无 output_url", file=sys.stderr)
            sys.exit(1)
        print(value)
        return

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
