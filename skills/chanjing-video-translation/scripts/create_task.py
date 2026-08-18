#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _api import api_post
from _auth import get_token


def build_payload(args):
    if args.body_file and args.body_json:
        raise ValueError("--body-file 和 --body-json 只能二选一")
    if args.body_file:
        return json.loads(Path(args.body_file).read_text(encoding="utf-8"))
    if args.body_json:
        return json.loads(args.body_json)
    if not args.target_language:
        raise ValueError("至少提供一个 --target-language")

    source = {key: value for key, value in (("video_id", args.video_id), ("file_id", args.file_id), ("title", args.title)) if value}
    if not source.get("video_id") and not source.get("file_id"):
        raise ValueError("提供 --video-id 或 --file-id")
    payload = {"source": source, "target_languages": args.target_language}
    if args.audio_id:
        payload["audio_id"] = args.audio_id
    for key in ("need_lip_sync", "need_dynamic_duration", "need_subtitle"):
        value = getattr(args, key)
        if value:
            payload[key] = True
    return payload


def main():
    parser = argparse.ArgumentParser(description="创建蝉镜视频翻译任务")
    parser.add_argument("--body-file", help="完整请求体 JSON 文件")
    parser.add_argument("--body-json", help="完整请求体 JSON 字符串")
    parser.add_argument("--video-id", help="已有源视频 ID")
    parser.add_argument("--file-id", help="已上传源文件 ID")
    parser.add_argument("--title", help="视频标题")
    parser.add_argument("--target-language", action="append", help="目标语言代码，可重复传参")
    parser.add_argument("--audio-id", help="输出音色 ID")
    parser.add_argument("--need-lip-sync", action="store_true", help="启用唇形驱动")
    parser.add_argument("--need-dynamic-duration", action="store_true", help="启用动态时长")
    parser.add_argument("--need-subtitle", action="store_true", help="生成字幕")
    args = parser.parse_args()
    try:
        payload = build_payload(args)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(str(exc))

    token, error = get_token()
    if error:
        raise SystemExit(error)
    print(json.dumps(api_post(token, "/open/v1/video_translation/create", payload), ensure_ascii=False))


if __name__ == "__main__":
    main()
