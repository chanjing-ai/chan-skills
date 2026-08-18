#!/usr/bin/env python3
"""
列出文生图、图生视频或 LoRA 任务列表。
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _auth import get_token
from _task_api import first_output_url, list_lora_tasks, list_motion_tasks, list_photo_tasks


def main():
    parser = argparse.ArgumentParser(description="列出文生数字人任务列表")
    parser.add_argument("--kind", choices=["photo", "motion", "lora"], default="photo", help="任务类型，默认 photo")
    parser.add_argument("--page", type=int, default=1, help="页码，默认 1")
    parser.add_argument("--page-size", type=int, default=10, help="每页数量，默认 10")
    parser.add_argument("--json", action="store_true", help="输出完整 JSON")
    args = parser.parse_args()

    token, err = get_token()
    if err:
        print(err, file=sys.stderr)
        sys.exit(1)

    try:
        fetch = {
            "photo": list_photo_tasks,
            "motion": list_motion_tasks,
            "lora": list_lora_tasks,
        }[args.kind]
        items = fetch(token, page=args.page, page_size=args.page_size)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(items, ensure_ascii=False))
        return

    for item in items or []:
        row = [
            item.get("unique_id") or item.get("lora_id", ""),
            str(item.get("type", "")),
            item.get("progress_desc", ""),
            str(item.get("waiting_num", "")),
            first_output_url(item) or "",
        ]
        print("\t".join(row))


if __name__ == "__main__":
    main()
