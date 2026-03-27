#!/usr/bin/env python3
"""
获取 LoRA 任务详情。
用法: get_lora_task.py --lora-id <id> [--field status]
默认输出: 完整 JSON
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _auth import get_token
from _task_api import get_lora_task


def main():
    parser = argparse.ArgumentParser(description="获取 LoRA 任务详情")
    parser.add_argument("--lora-id", required=True, help="LoRA 任务 ID")
    parser.add_argument("--field", help="只输出某个字段")
    args = parser.parse_args()

    token, err = get_token()
    if err:
        print(err, file=sys.stderr)
        sys.exit(1)

    try:
        data = get_lora_task(token, args.lora_id)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

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
