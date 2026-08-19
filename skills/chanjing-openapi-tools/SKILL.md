---
name: chanjing-openapi-tools
description: 查询蝉镜标签、消耗、价格，管理分片上传或生成创意 Briefing 时使用。需要已配置的蝉镜 OpenAPI AK/SK。
---

# Chanjing OpenAPI Tools

## When to Use This Skill

用于非媒体生成工作流的开放平台工具：查询公共资源标签、消耗明细、价格目录，创建或完成分片上传，以及按商品生成创意雷达 Briefing。

## Covered APIs

* `GET /open/v1/tag_list`
* `POST /open/v1/consume_detail`
* `GET /open/v1/price/catalog`
* `POST /open/v1/common/create_multipart_upload`
* `POST /open/v1/common/complete_multipart_upload`
* `GET /open/v1/common/file_detail`
* `POST /open/v1/creative/creative_briefing`

## Scripts

```bash
python3 skills/chanjing-openapi-tools/scripts/openapi_tools.py consume-detail \
  --start-time '2026-08-01 00:00:00' --end-time '2026-08-02 00:00:00'
python3 skills/chanjing-openapi-tools/scripts/openapi_tools.py price-catalog --item-code <item_code>
python3 skills/chanjing-openapi-tools/scripts/openapi_tools.py create-multipart-upload \
  --file-size 1048576 --name source.mp4 --service video
python3 skills/chanjing-openapi-tools/scripts/openapi_tools.py complete-multipart-upload --upload-id <upload_id>
python3 skills/chanjing-openapi-tools/scripts/openapi_tools.py file-detail --id <file_id>
python3 skills/chanjing-openapi-tools/scripts/openapi_tools.py creative-briefing \
  --product-name '产品名称' --creative-hint '卖点方向'
```

全部命令输出接口 `data` 的 JSON。分片上传的具体分片传输按创建接口返回的签名和分片规则执行；本 Skill 不直接读取或上传本地文件。
