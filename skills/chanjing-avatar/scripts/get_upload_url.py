#!/usr/bin/env python3
"""
获取上传链接。与 chanjing-credentials-guard 使用同一配置文件获取 Token。
用法: get_upload_url.py --service lip_sync_video --name 1.mp4
输出: JSON { "sign_url", "mime_type", "file_id" } 或错误到 stderr
"""
import argparse
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

# 同目录 _auth
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _auth import get_token

API_BASE = (__import__("os").environ.get("CHANJING_OPENAPI_BASE_URL") or __import__("os").environ.get("CHANJING_API_BASE") or "https://open-api.chanjing.cc").rstrip("/")


def main():
    parser = argparse.ArgumentParser(description="获取蝉镜文件上传链接")
    parser.add_argument("--service", required=True, help="lip_sync_video 或 lip_sync_audio")
    parser.add_argument("--name", required=True, help="文件名，如 1.mp4")
    args = parser.parse_args()

    token, err = get_token()
    if err:
        print(err, file=sys.stderr)
        sys.exit(1)

    qs = urllib.parse.urlencode({"service": args.service, "name": args.name})
    url = f"{API_BASE}/open/v1/common/create_upload_url?{qs}"
    req = urllib.request.Request(url, headers={"access_token": token}, method="GET")
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode("utf-8"))

    if body.get("code") != 0:
        print(body.get("msg", body), file=sys.stderr)
        sys.exit(1)

    data = body.get("data", {})
    print(json.dumps(data, ensure_ascii=False))


if __name__ == "__main__":
    main()
