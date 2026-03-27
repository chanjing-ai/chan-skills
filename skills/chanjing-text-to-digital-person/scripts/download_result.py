#!/usr/bin/env python3
"""
下载文生数字人生成结果到本地。
用法:
  download_result --url https://example.com/output.png
  download_result --url https://example.com/output.mp4 --output outputs/text-to-digital-person/demo.mp4
输出: 本地文件路径
"""
from __future__ import annotations

import argparse
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path


def infer_filename(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    name = Path(parsed.path).name or "text-to-digital-person.bin"
    if "." not in name:
        name += ".bin"
    return name


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="下载蝉镜文生数字人生成结果到本地目录")
    parser.add_argument("--url", required=True, help="图片或视频输出地址")
    parser.add_argument(
        "--output",
        help="输出文件路径；默认保存到 outputs/text-to-digital-person/<文件名>",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    default_dir = Path("outputs") / "text-to-digital-person"
    output_path = Path(args.output) if args.output else default_dir / infer_filename(args.url)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    req = urllib.request.Request(
        args.url,
        headers={"User-Agent": "chanjing-text-to-digital-person-downloader"},
        method="GET",
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp, open(output_path, "wb") as handle:
            handle.write(resp.read())
    except Exception as exc:
        print(f"下载失败: {exc}", file=sys.stderr)
        raise SystemExit(1)

    if not output_path.exists() or output_path.stat().st_size == 0:
        print("下载失败: 输出文件为空", file=sys.stderr)
        raise SystemExit(1)

    print(os.fspath(output_path))


if __name__ == "__main__":
    main()
