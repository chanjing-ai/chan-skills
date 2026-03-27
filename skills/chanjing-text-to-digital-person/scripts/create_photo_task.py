#!/usr/bin/env python3
"""
创建文生图任务。
用法:
  create_photo_task --age "Young adult" --gender Female --number-of-images 1 [其他提示词]
输出: 文生图任务 unique_id
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _auth import get_token
from _task_api import api_post


def main():
    parser = argparse.ArgumentParser(description="创建蝉镜文生图任务")
    parser.add_argument("--age", required=True, help="Young adult / Adult / Teenager / Elderly")
    parser.add_argument("--gender", required=True, choices=["Male", "Female"], help="性别")
    parser.add_argument("--number-of-images", required=True, type=int, choices=[1, 2, 3, 4], help="生成图片张数")
    parser.add_argument("--background", help="背景提示词")
    parser.add_argument("--detail", help="细节提示词")
    parser.add_argument("--talking-pose", help="讲话姿势提示词")
    parser.add_argument("--industry", help="行业提示词")
    parser.add_argument("--origin", help="人种提示词，例如 Chinese / European")
    parser.add_argument("--aspect-ratio", type=int, choices=[0, 1], default=0, help="0=9:16, 1=16:9")
    parser.add_argument("--ref-img-url", help="参考图链接")
    parser.add_argument("--ref-content", choices=["style", "appearance"], help="参考内容类型")
    args = parser.parse_args()

    body = {
        "age": args.age,
        "gender": args.gender,
        "number_of_images": args.number_of_images,
        "aspect_ratio": args.aspect_ratio,
    }
    if args.background:
        body["background"] = args.background
    if args.detail:
        body["detail"] = args.detail
    if args.talking_pose:
        body["talking_pose"] = args.talking_pose
    if args.industry:
        body["industry"] = args.industry
    if args.origin:
        body["origin"] = args.origin
    if args.ref_img_url:
        body["ref_img_url"] = args.ref_img_url
    if args.ref_content:
        body["ref_content"] = args.ref_content

    token, err = get_token()
    if err:
        print(err, file=sys.stderr)
        sys.exit(1)

    try:
        unique_id = api_post(token, "/open/v1/aigc/photo", body)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

    if not unique_id:
        print("响应无文生图任务 ID", file=sys.stderr)
        sys.exit(1)
    print(unique_id)


if __name__ == "__main__":
    main()
