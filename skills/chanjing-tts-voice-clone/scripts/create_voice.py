#!/usr/bin/env python3
"""
创建定制声音（声音克隆）。需提供参考音频的公开 URL。
与 chanjing-credentials-guard 使用同一配置文件；无 AK/SK 时执行 open_login_page.py 打开登录页。
用法: create_voice.py --name "我的声音" --url "https://example.com/ref.mp3" [--model-type Cicada3.0-turbo] [--language cn]
输出: voice_id（一行）或错误到 stderr
"""
import argparse
import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _auth import get_token

API_BASE = (__import__("os").environ.get("CHANJING_OPENAPI_BASE_URL") or __import__("os").environ.get("CHANJING_API_BASE") or "https://open-api.chanjing.cc").rstrip("/")


def main():
    parser = argparse.ArgumentParser(description="创建定制声音（参考音频 URL）")
    parser.add_argument("--name", required=True, help="声音名称")
    parser.add_argument("--url", required=True, help="参考音频的公开 URL（mp3/wav/m4a，建议 30s–5min）")
    parser.add_argument("--model-type", default="Cicada3.0-turbo", help="模型类型，默认 Cicada3.0-turbo")
    parser.add_argument("--language", default="cn", help="cn 或 en，默认 cn")
    args = parser.parse_args()

    body = {
        "name": args.name,
        "url": args.url,
        "model_type": args.model_type,
        "language": args.language,
    }

    token, err = get_token()
    if err:
        print(err, file=sys.stderr)
        sys.exit(1)

    url = f"{API_BASE}/open/v1/create_customised_audio"
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"access_token": token, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        res = json.loads(resp.read().decode("utf-8"))

    if res.get("code") != 0:
        print(res.get("msg", res), file=sys.stderr)
        sys.exit(1)

    voice_id = res.get("data")
    if not voice_id:
        print("响应无 data（voice_id）", file=sys.stderr)
        sys.exit(1)
    print(voice_id)


if __name__ == "__main__":
    main()
