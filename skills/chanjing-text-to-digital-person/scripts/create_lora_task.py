#!/usr/bin/env python3
"""
创建 LoRA 训练任务。
用法:
  create_lora_task --name "我的LoRA" --photo-url https://a/1.jpg --photo-url https://a/2.jpg ...
输出: lora_id
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _auth import get_token
from _task_api import api_post


def main():
    parser = argparse.ArgumentParser(description="创建文生数字人 LoRA 任务")
    parser.add_argument("--name", required=True, help="LoRA 名称")
    parser.add_argument("--photo-url", action="append", required=True, help="训练照片 URL，至少 5 张，可重复传参")
    parser.add_argument("--lora-id", help="失败任务重试时传入已有 lora_id")
    args = parser.parse_args()

    if len(args.photo_url) < 5 or len(args.photo_url) > 50:
        print("照片素材数量必须在 5 到 50 张之间", file=sys.stderr)
        sys.exit(1)

    body = {
        "name": args.name,
        "photos": args.photo_url,
    }
    if args.lora_id:
        body["lora_id"] = args.lora_id

    token, err = get_token()
    if err:
        print(err, file=sys.stderr)
        sys.exit(1)

    try:
        data = api_post(token, "/open/v1/aigc/lora/task/create", body)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

    lora_id = (data or {}).get("lora_id")
    if not lora_id:
        print("响应无 lora_id", file=sys.stderr)
        sys.exit(1)
    print(lora_id)


if __name__ == "__main__":
    main()
