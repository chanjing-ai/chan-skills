---
name: chanjing-customised-person
description: Use Chanjing customised person APIs to create, inspect, list, poll, and delete custom digital humans from uploaded source videos.
---

# Chanjing Customised Person

## When to Use This Skill

当用户要做这些事时使用本 Skill：

* 上传真人源视频，创建蝉镜定制数字人
* 查询定制数字人列表或单个形象详情
* 轮询定制数字人制作进度
* 删除不再需要的定制数字人

如果需求是“拿已有数字人去合成口播视频”，优先使用 `chanjing-video-compose`。  
如果需求是“上传真人视频做对口型驱动”，优先使用 `chanjing-avatar`。

## Preconditions

执行本 Skill 前，必须先通过 `chanjing-credentials-guard` 完成 AK/SK 与 Token 校验。

本 Skill 与 guard 共用：

* `~/.chanjing/credentials.json`
* `https://open-api.chanjing.cc`

无凭证时，脚本会自动打开蝉镜登录页，并提示配置命令。

## Standard Workflow

1. 调用 `upload_file` 上传本地源视频，获取 `file_id`
2. 调用 `create_person` 创建定制数字人任务，得到 `person_id`
3. 调用 `poll_person` 轮询直到成功，得到 `preview_url`，或用 `get_person --field audio_man_id` 拿到声音 id
4. 如需批量查看历史形象，用 `list_persons`
5. 如需清理资源，用 `delete_person`

## Covered APIs

本 Skill 当前覆盖：

* `GET /open/v1/common/create_upload_url`
* `GET /open/v1/common/file_detail`
* `POST /open/v1/create_customised_person`
* `POST /open/v1/list_customised_person`
* `GET /open/v1/customised_person`
* `POST /open/v1/delete_customised_person`

## Scripts

脚本目录：

* `skills/chanjing-customised-person/scripts/`

| 脚本 | 说明 |
|------|------|
| `_auth.py` | 读取凭证、获取或刷新 `access_token` |
| `get_upload_url` | 获取上传链接，输出 `sign_url`、`mime_type`、`file_id` 等 JSON |
| `upload_file` | 上传本地素材并轮询到文件可用，输出 `file_id` |
| `create_person` | 创建定制数字人任务，输出 `person_id` |
| `list_persons` | 列出定制数字人形象 |
| `get_person` | 获取单个数字人详情，默认输出 JSON |
| `poll_person` | 轮询形象详情直到完成，默认输出 `preview_url` |
| `delete_person` | 删除定制数字人，输出被删除的 `person_id` |

## Usage Examples

示例 1：从本地视频创建定制数字人

```bash
FILE_ID=$(python3 skills/chanjing-customised-person/scripts/upload_file \
  --file ./source.mp4)

PERSON_ID=$(python3 skills/chanjing-customised-person/scripts/create_person \
  --name "演示数字人" \
  --file-id "$FILE_ID" \
  --train-type figure)

python3 skills/chanjing-customised-person/scripts/poll_person --id "$PERSON_ID"
```

示例 2：查看完整详情

```bash
python3 skills/chanjing-customised-person/scripts/get_person \
  --id "C-ef91f3a6db3144ffb5d6c581ff13c7ec"
```

示例 3：列出与删除

```bash
python3 skills/chanjing-customised-person/scripts/list_persons

python3 skills/chanjing-customised-person/scripts/delete_person \
  --id "C-ef91f3a6db3144ffb5d6c581ff13c7ec"
```

## Output Convention

默认不自动下载任何预览视频或封面图：

* `create_person` 输出 `person_id`
* `poll_person` 输出 `preview_url`，便于继续预览或保存
* 只有在用户明确要求时，才应把返回的资源 URL 另存到本地

如果后续需要落盘预览资源，建议使用：

* `outputs/customised-person/`

## Additional Resources

更多接口细节与触发样例见：

* `skills/chanjing-customised-person/reference.md`
* `skills/chanjing-customised-person/examples.md`
