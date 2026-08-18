---
name: chanjing-video-translation
description: 创建蝉镜视频翻译任务或查询支持语言时使用。需要已配置的蝉镜 OpenAPI AK/SK。
---

# Chanjing Video Translation

## When to Use This Skill

用于把已上传的视频或已有视频任务翻译为一个或多个目标语言。先用 `list_target_languages.py` 确认语言代码，再创建任务。

## Preconditions

配置 `credentials.json`，缺失时先运行 `chanjing-credentials-guard`。源素材使用已有 `video_id` 或 `file_id`；不在本 Skill 内上传文件。

## Covered APIs

* `GET /open/v1/video_translation/target_languages`
* `POST /open/v1/video_translation/create`

## Scripts

```bash
# 查询可用目标语言
python3 skills/chanjing-video-translation/scripts/list_target_languages.py

# 按已有文件创建翻译任务
python3 skills/chanjing-video-translation/scripts/create_task.py \
  --file-id <file_id> --target-language en --target-language ja

# 透传完整请求体，适合音色、字幕和唇形参数
python3 skills/chanjing-video-translation/scripts/create_task.py \
  --body-file ./video-translation.json
```

`--body-file` 与 `--body-json` 可传完整 OpenAPI 请求体。常用字段包括 `source.video_id`、`source.file_id`、`target_languages`、`audio_id`、`need_lip_sync`、`need_dynamic_duration` 和 `need_subtitle`。

## Boundary

该能力当前只同步 OpenAPI 已公开的创建和语言查询接口；任务详情或轮询接口不在 api-mcp 当前能力范围内。
