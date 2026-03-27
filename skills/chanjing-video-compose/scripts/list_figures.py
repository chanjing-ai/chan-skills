#!/usr/bin/env python3
"""
列出可用于视频合成的数字人形象。
用法: list_figures.py [--source customised|common] [--page 1] [--page-size 20] [--json]
输出: 默认打印摘要表；--json 时输出完整 data
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


def fetch_customised(token, page, page_size):
    body = json.dumps({"page": page, "page_size": page_size}).encode("utf-8")
    req = urllib.request.Request(
        f"{API_BASE}/open/v1/list_customised_person",
        data=body,
        headers={"access_token": token, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_common(token, page, page_size):
    params = urllib.parse.urlencode({"page": page, "size": page_size})
    req = urllib.request.Request(
        f"{API_BASE}/open/v1/list_common_dp?{params}",
        headers={"access_token": token, "Content-Type": "application/json"},
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def build_rows(source, items):
    rows = []
    if source == "customised":
        for item in items:
            width = item.get("width")
            height = item.get("height")
            size = f"{width}x{height}" if width and height else "-"
            rows.append(
                {
                    "source": "customised",
                    "person_id": item.get("id", ""),
                    "name": item.get("name", ""),
                    "figure_type": "-",
                    "size": size,
                    "audio_man_id": item.get("audio_man_id", ""),
                    "note": f"support_4k={item.get('support_4k', '')}",
                    "preview_url": item.get("preview_url", ""),
                }
            )
        return rows

    for item in items:
        for figure in item.get("figures", []):
            rows.append(
                {
                    "source": "common",
                    "person_id": item.get("id", ""),
                    "name": item.get("name", ""),
                    "figure_type": figure.get("type", ""),
                    "size": f"{figure.get('width', '')}x{figure.get('height', '')}",
                    "audio_man_id": item.get("audio_man_id", ""),
                    "note": f"audio_name={item.get('audio_name', '')}",
                    "preview_url": figure.get("preview_video_url", ""),
                }
            )
    return rows


def main():
    parser = argparse.ArgumentParser(description="列出蝉镜视频合成可用数字人形象")
    parser.add_argument(
        "--source",
        choices=["customised", "common"],
        default="customised",
        help="数字人来源：customised 为定制数字人，common 为公共数字人",
    )
    parser.add_argument("--page", type=int, default=1, help="页码")
    parser.add_argument("--page-size", type=int, default=20, help="每页数量")
    parser.add_argument("--json", action="store_true", help="输出完整 JSON")
    args = parser.parse_args()

    token, err = get_token()
    if err:
        print(err, file=sys.stderr)
        sys.exit(1)

    if args.source == "customised":
        res = fetch_customised(token, args.page, args.page_size)
    else:
        res = fetch_common(token, args.page, args.page_size)

    if res.get("code") != 0:
        print(res.get("msg", res), file=sys.stderr)
        sys.exit(1)

    data = res.get("data", {})
    if args.json:
        print(json.dumps({"source": args.source, "data": data}, ensure_ascii=False, indent=2))
        return

    items = data.get("list", [])
    page_info = data.get("page_info", {})
    rows = build_rows(args.source, items)
    print(f"# source={args.source} 共 {page_info.get('total_count', len(items))} 个形象 (page={args.page})")
    print(
        f"{'source':<10}  {'person_id':<36}  {'name':<14}  {'figure_type':<12}  "
        f"{'size':<11}  {'audio_man_id':<36}  {'note':<24}  preview_url"
    )
    print("-" * 220)
    for row in rows:
        print(
            f"{row['source']:<10}  "
            f"{row['person_id']:<36}  "
            f"{row['name']:<14}  "
            f"{row['figure_type']:<12}  "
            f"{row['size']:<11}  "
            f"{row['audio_man_id']:<36}  "
            f"{row['note']:<24}  "
            f"{row['preview_url']}"
        )


if __name__ == "__main__":
    main()
