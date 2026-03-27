#!/usr/bin/env python3
"""
获取定制数字人素材上传链接（create_upload_url）。
客户端需自行对返回的 sign_url 执行 PUT 上传；sign_url 主机由接口决定，可能与 Open API 域不同。
用法: get_upload_url.py --name source.mp4 [--service customised_person]
输出: JSON，包含 sign_url / mime_type / file_id
"""
import argparse
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _auth import get_token

API_BASE = (__import__("os").environ.get("CHANJING_OPENAPI_BASE_URL") or __import__("os").environ.get("CHANJING_API_BASE") or "https://open-api.chanjing.cc").rstrip("/")


def main():
    parser = argparse.ArgumentParser(description="获取定制数字人素材上传链接")
    parser.add_argument("--name", required=True, help="原始文件名，如 source.mp4")
    parser.add_argument(
        "--service",
        default="customised_person",
        help="文件用途，默认 customised_person",
    )
    args = parser.parse_args()

    token, err = get_token()
    if err:
        print(err, file=sys.stderr)
        sys.exit(1)

    query = urllib.parse.urlencode({"service": args.service, "name": args.name})
    url = f"{API_BASE}/open/v1/common/create_upload_url?{query}"
    req = urllib.request.Request(url, headers={"access_token": token}, method="GET")
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode("utf-8"))

    if body.get("code") != 0:
        print(body.get("msg", body), file=sys.stderr)
        sys.exit(1)

    print(json.dumps(body.get("data", {}), ensure_ascii=False))


if __name__ == "__main__":
    main()
