#!/usr/bin/env python3
"""
创建图生视频任务。
用法: create_motion_task.py --photo-unique-id <photo_task_id> --photo-path <image_url> [--emotion ...] [--gesture]
输出: 图生视频任务 unique_id
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _auth import get_token
from _task_api import api_post


def main():
    parser = argparse.ArgumentParser(description="创建图生视频任务")
    parser.add_argument("--photo-unique-id", required=True, help="来源文生图任务 ID")
    parser.add_argument("--photo-path", required=True, help="图片地址")
    parser.add_argument("--emotion", help="情感提示词")
    parser.add_argument("--gesture", action="store_true", help="启用动作")
    args = parser.parse_args()

    body = {
        "photo_unique_id": args.photo_unique_id,
        "photo_path": args.photo_path,
        "gesture": args.gesture,
    }
    if args.emotion:
        body["emotion"] = args.emotion

    token, err = get_token()
    if err:
        print(err, file=sys.stderr)
        sys.exit(1)

    try:
        unique_id = api_post(token, "/open/v1/aigc/motion", body)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

    if not unique_id:
        print("响应无图生视频任务 ID", file=sys.stderr)
        sys.exit(1)
    print(unique_id)


if __name__ == "__main__":
    main()
