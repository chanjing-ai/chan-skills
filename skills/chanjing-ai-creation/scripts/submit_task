#!/usr/bin/env python3
"""
提交 AI 创作任务。

推荐两种方式：
1. 通用参数模式：
   submit_task --creation-type 3 --model-code doubao-seedream-3.0-t2i --prompt "..." --number-of-images 1
2. 原始 JSON 模式：
   submit_task --body-file ./payload.json
   submit_task --body-json '{"creation_type":3,...}'
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _auth import get_token
from _task_api import api_post


def load_body(args):
    if args.body_file and args.body_json:
        raise ValueError("--body-file 和 --body-json 只能二选一")

    if args.body_file:
        with open(args.body_file, "r", encoding="utf-8") as f:
            return json.load(f)

    if args.body_json:
        return json.loads(args.body_json)

    if not args.creation_type or not args.model_code:
        raise ValueError("通用参数模式下必须提供 --creation-type 和 --model-code")

    body = {
        "creation_type": args.creation_type,
        "model_code": args.model_code,
    }

    if args.prompt:
        body["ref_prompt"] = args.prompt
    if args.aspect_ratio:
        body["aspect_ratio"] = args.aspect_ratio
    if args.clarity is not None:
        body["clarity"] = args.clarity
    if args.quality_mode:
        body["quality_mode"] = args.quality_mode
    if args.number_of_images is not None:
        body["number_of_images"] = args.number_of_images
    if args.video_duration is not None:
        body["video_duration"] = args.video_duration
    if args.style:
        body["style"] = args.style
    if args.callback:
        body["callback"] = args.callback
    if args.ref_img_url:
        body["ref_img_url"] = args.ref_img_url

    return body


def main():
    parser = argparse.ArgumentParser(description="提交蝉镜 AI 创作任务")
    parser.add_argument("--body-file", help="完整请求体 JSON 文件路径")
    parser.add_argument("--body-json", help="完整请求体 JSON 字符串")
    parser.add_argument("--creation-type", type=int, choices=[3, 4], help="3=图片生成，4=视频生成")
    parser.add_argument("--model-code", help="模型编码")
    parser.add_argument("--prompt", help="提示词，对应 ref_prompt")
    parser.add_argument("--ref-img-url", action="append", help="参考图 URL，可重复传参")
    parser.add_argument("--aspect-ratio", help="比例，如 1:1 / 3:4 / 4:3 / 9:16 / 16:9")
    parser.add_argument("--clarity", type=int, help="清晰度，如 1024/2048/4096 或 720/1080")
    parser.add_argument("--quality-mode", help="质量模式，如 std / pro")
    parser.add_argument("--number-of-images", type=int, help="图片生成数量，1-4")
    parser.add_argument("--video-duration", type=int, help="视频时长（秒）")
    parser.add_argument("--style", help="部分视频模型支持的视频风格")
    parser.add_argument("--callback", help="任务完成回调 URL")
    args = parser.parse_args()

    try:
        body = load_body(args)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

    token, err = get_token()
    if err:
        print(err, file=sys.stderr)
        sys.exit(1)

    try:
        unique_id = api_post(token, "/open/v1/ai_creation/task/submit", body)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

    if not unique_id:
        print("响应无任务 unique_id", file=sys.stderr)
        sys.exit(1)
    print(unique_id)


if __name__ == "__main__":
    main()
