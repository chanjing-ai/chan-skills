---
name: chanjing-video-compose
description: Use Chanjing video synthesis APIs to create digital human videos from text or audio, with optional background upload, task polling, and explicit download when the user asks to save the result locally.
---

# Chanjing Video Compose

## When to Use This Skill

当用户要做这些事时使用本 Skill：

* 创建数字人视频合成任务
* 用文本驱动数字人出镜
* 用本地音频驱动数字人视频
* 查询可用数字人形象
* 轮询视频合成结果
* 在用户明确要求时下载最终视频到本地

如果需求更接近“上传一段真人视频做对口型驱动”，优先使用 `chanjing-avatar`，不要混用。

## Preconditions

执行本 Skill 前，必须先通过 `chanjing-credentials-guard` 完成 AK/SK 与 Token 校验。

本 Skill 与 guard 共用：

* `~/.chanjing/credentials.json`
* `https://open-api.chanjing.cc`

无凭证时，脚本会自动打开蝉镜登录页，并提示配置命令。

## Standard Workflow

1. 调用 `list_figures` 获取可用数字人形象，选定 `person.id`
2. 若使用文本驱动，确定 `audio_man_id`
3. 若使用本地音频或背景图，先调用 `upload_file` 获取 `file_id`
4. 调用 `create_task` 创建视频合成任务，得到 `video_id`
5. 调用 `poll_task` 轮询直到成功，得到 `video_url`
6. 只有在用户明确要求保存到本地时，才调用 `download_result`

## Covered APIs

本 Skill 当前覆盖：

* `POST /open/v1/list_customised_person`
* `POST /open/v1/create_video`
* `GET /open/v1/video`
* `GET /open/v1/common/create_upload_url`
* `GET /open/v1/common/file_detail`

## Scripts

脚本目录：

* `skills/chanjing-video-compose/scripts/`

| 脚本 | 说明 |
|------|------|
| `_auth.py` | 读取凭证、获取或刷新 `access_token` |
| `list_figures` | 列出数字人形象，输出 `id` / `audio_man_id` / `support_4k` |
| `upload_file` | 上传音频或背景素材，轮询到文件可用后输出 `file_id` |
| `create_task` | 创建视频合成任务，输出 `video_id` |
| `poll_task` | 轮询视频详情直到完成，默认输出 `video_url` |
| `download_result` | 下载最终视频到 `outputs/video-compose/` |

## Usage Examples

示例 1：文本驱动

```bash
# 1. 列出可用形象
python skills/chanjing-video-compose/scripts/list_figures

# 2. 创建文本驱动视频
VIDEO_ID=$(python skills/chanjing-video-compose/scripts/create_task \
  --person-id "C-ef91f3a6db3144ffb5d6c581ff13c7ec" \
  --audio-man "C-0ae461135d8a4eb2b59c853162ea9848" \
  --text "你好，这是一个蝉镜视频合成测试。")

# 3. 轮询到完成，拿到 video_url
python skills/chanjing-video-compose/scripts/poll_task --id "$VIDEO_ID"
```

示例 2：上传本地音频驱动

```bash
AUDIO_FILE_ID=$(python skills/chanjing-video-compose/scripts/upload_file \
  --service make_video_audio \
  --file ./input.wav)

VIDEO_ID=$(python skills/chanjing-video-compose/scripts/create_task \
  --person-id "C-ef91f3a6db3144ffb5d6c581ff13c7ec" \
  --audio-file-id "$AUDIO_FILE_ID")

python skills/chanjing-video-compose/scripts/poll_task --id "$VIDEO_ID"
```

示例 3：显式下载最终视频

```bash
python skills/chanjing-video-compose/scripts/download_result \
  --url "https://example.com/output.mp4"
```

## Download Rule

下载是显式动作，不是默认动作：

* `poll_task` 成功后应先返回 `video_url`
* 不要自动下载结果文件
* 只有当用户明确表达“下载到本地”“保存到 outputs”“帮我落盘”时，才执行 `download_result`

## Output Convention

默认本地输出目录：

* `outputs/video-compose/`

## Additional Resources

更多接口细节见：

* `skills/chanjing-video-compose/reference.md`
* `skills/chanjing-video-compose/examples.md`
