#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _api import api_get, api_post
from _auth import get_token


def build_parser():
    parser = argparse.ArgumentParser(description="蝉镜 OpenAPI 通用工具")
    commands = parser.add_subparsers(dest="command", required=True)
    tag = commands.add_parser("tag-list", help="查询公共数字人与声音标签")
    tag.add_argument("--business-type", type=int, action="append", help="业务类型，可重复传参")
    price = commands.add_parser("price-catalog", help="查询公开价格目录")
    price.add_argument("--item-code", help="计费项编码")
    consume = commands.add_parser("consume-detail", help="查询蝉豆消耗明细")
    consume.add_argument("--start-time", required=True, help="开始时间，例如 2026-08-01 00:00:00")
    consume.add_argument("--end-time", required=True, help="结束时间，最多间隔 31 天")
    consume.add_argument("--consume-type", help="消耗类型")
    consume.add_argument("--page", type=int, help="页码")
    consume.add_argument("--page-size", type=int, help="每页大小")
    create = commands.add_parser("create-multipart-upload", help="创建分片上传任务")
    create.add_argument("--file-size", type=int, required=True, help="文件字节数")
    create.add_argument("--name", required=True, help="文件名")
    create.add_argument("--service", required=True, help="文件用途")
    complete = commands.add_parser("complete-multipart-upload", help="完成分片上传")
    complete.add_argument("--upload-id", required=True, help="上传任务 ID")
    file_detail = commands.add_parser("file-detail", help="查询文件详情")
    file_detail.add_argument("--id", required=True, help="文件 ID")
    briefing = commands.add_parser("creative-briefing", help="生成创意雷达品类 Briefing")
    briefing.add_argument("--product-name", required=True, help="商品名")
    briefing.add_argument("--creative-hint", help="创意提示")
    briefing.add_argument("--top-product-count", type=int, help="头部商品数量")
    briefing.add_argument("--top-category-count", type=int, help="头部品类数量")
    briefing.add_argument("--awemes-per-category", type=int, help="每个品类视频数量")
    return parser


def invoke(args, token):
    if args.command == "tag-list":
        query = {"business_type": args.business_type} if args.business_type else None
        return api_get(token, "/open/v1/tag_list", query)
    if args.command == "price-catalog":
        query = {"item_code": args.item_code} if args.item_code else None
        return api_get(token, "/open/v1/price/catalog", query)
    if args.command == "consume-detail":
        payload = {"start_time": args.start_time, "end_time": args.end_time}
        for key in ("consume_type", "page", "page_size"):
            value = getattr(args, key)
            if value is not None:
                payload[key] = value
        return api_post(token, "/open/v1/consume_detail", payload)
    if args.command == "create-multipart-upload":
        return api_post(token, "/open/v1/common/create_multipart_upload", {"file_size": args.file_size, "name": args.name, "service": args.service})
    if args.command == "complete-multipart-upload":
        return api_post(token, "/open/v1/common/complete_multipart_upload", {"upload_id": args.upload_id})
    if args.command == "file-detail":
        return api_get(token, "/open/v1/common/file_detail", {"id": args.id})
    if args.command == "creative-briefing":
        payload = {"product_name": args.product_name}
        for key in ("creative_hint", "top_product_count", "top_category_count", "awemes_per_category"):
            value = getattr(args, key)
            if value is not None:
                payload[key] = value
        return api_post(token, "/open/v1/creative/creative_briefing", payload)
    raise ValueError(f"未知命令: {args.command}")


def main():
    args = build_parser().parse_args()
    token, error = get_token()
    if error:
        raise SystemExit(error)
    try:
        print(json.dumps(invoke(args, token), ensure_ascii=False))
    except Exception as exc:
        raise SystemExit(str(exc))


if __name__ == "__main__":
    main()
