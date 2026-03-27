#!/usr/bin/env python3
"""
上传视频合成所需文件并轮询直到就绪，最后输出 file_id。
与 chanjing-credentials-guard 使用同一配置文件获取 Token。
用法:
  upload_file --service make_video_audio --file /path/to/input.wav
  upload_file --service make_video_background --file /path/to/bg.png
输出: file_id（一行）或错误到 stderr
"""
import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _auth import get_token

API_BASE = (__import__("os").environ.get("CHANJING_OPENAPI_BASE_URL") or __import__("os").environ.get("CHANJING_API_BASE") or "https://open-api.chanjing.cc").rstrip("/")
FILE_READY_STATUSES = {1}
FILE_FAILED_STATUSES = {98, 99, 100}
POLL_INTERVAL_DEFAULT = 5
POLL_TIMEOUT_DEFAULT = 300


def get_file_detail(token, file_id):
    url = f"{API_BASE}/open/v1/common/file_detail?id={urllib.parse.quote(file_id)}"
    req = urllib.request.Request(url, headers={"access_token": token}, method="GET")
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    if body.get("code") != 0:
        return None, body.get("msg", "file_detail failed")
    return body.get("data"), None


def poll_file_ready(token, file_id, interval=5, timeout=300):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        data, err = get_file_detail(token, file_id)
        if err:
            return False, err
        if data is None:
            return False, "no data"

        status = data.get("status")
        if status in FILE_READY_STATUSES:
            return True, None
        if status in FILE_FAILED_STATUSES:
            return False, data.get("msg") or f"file status={status}"

        time.sleep(interval)
    return False, "poll timeout"


def main():
    parser = argparse.ArgumentParser(description="上传视频合成文件并轮询直到就绪，返回 file_id")
    parser.add_argument(
        "--service",
        required=True,
        choices=["make_video_audio", "make_video_background", "ai_creation"],
        help="文件用途：音频、背景素材或 AI 创作",
    )
    parser.add_argument("--file", required=True, help="本地文件路径")
    parser.add_argument("--poll-interval", type=int, default=POLL_INTERVAL_DEFAULT, help="轮询间隔秒数")
    parser.add_argument("--poll-timeout", type=int, default=POLL_TIMEOUT_DEFAULT, help="轮询超时秒数")
    args = parser.parse_args()

    path = Path(args.file)
    if not path.is_file():
        print(f"文件不存在: {path}", file=sys.stderr)
        sys.exit(1)

    token, err = get_token()
    if err:
        print(err, file=sys.stderr)
        sys.exit(1)

    qs = urllib.parse.urlencode({"service": args.service, "name": path.name})
    url = f"{API_BASE}/open/v1/common/create_upload_url?{qs}"
    req = urllib.request.Request(url, headers={"access_token": token}, method="GET")
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode("utf-8"))

    if body.get("code") != 0:
        print(body.get("msg", body), file=sys.stderr)
        sys.exit(1)

    data = body.get("data", {})
    sign_url = data.get("sign_url")
    mime_type = data.get("mime_type", "application/octet-stream")
    file_id = data.get("file_id")

    if not sign_url or not file_id:
        print("响应缺少 sign_url 或 file_id", file=sys.stderr)
        sys.exit(1)

    with open(path, "rb") as f:
        content = f.read()
    put_req = urllib.request.Request(
        sign_url,
        data=content,
        headers={"Content-Type": mime_type},
        method="PUT",
    )
    try:
        with urllib.request.urlopen(put_req, timeout=120) as put_resp:
            if put_resp.status not in (200, 204):
                print(f"上传返回状态: {put_resp.status}", file=sys.stderr)
                sys.exit(1)
    except Exception as exc:
        print(f"上传失败: {exc}", file=sys.stderr)
        sys.exit(1)

    ready, err = poll_file_ready(token, file_id, interval=args.poll_interval, timeout=args.poll_timeout)
    if not ready:
        print(f"文件未就绪: {err}", file=sys.stderr)
        sys.exit(1)

    print(file_id)


if __name__ == "__main__":
    main()
