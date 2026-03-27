---
name: chanjing-video-compose
description: >-
  Use Chanjing video synthesis APIs to create digital human videos from text or
  audio, with optional background upload, polling, and explicit download.
credential: credentials.json (app_id/secret_key; access_token persisted on disk; same file as chanjing-credentials-guard)
openclaw_primary_env: false
environment: CHANJING_OPENAPI_CREDENTIALS_DIR, CHANJING_OPENAPI_BASE_URL
legacy_environment: CHANJING_CONFIG_DIR, CHANJING_API_BASE
machine_readable: manifest.yaml
requires_ffmpeg: false
requires_ffprobe: false
notes: >-
  May invoke open_login_page.py when AK/SK missing. create_task.py optional
  --callback may POST task results to a user-supplied URL.
---

# Chanjing Video Compose

## 功能说明

调用蝉镜**视频合成** Open API：列举公共/定制形象、上传素材、文本或音频驱动数字人、轮询任务；用户明确要求时用脚本下载成片。本 skill 脚本**不**依赖 ffmpeg/ffprobe（与一键成片编排不同）。凭据与权限边界见同目录 **`manifest.yaml`**。

## 运行依赖

- **python3** 与同仓库 `scripts/*.py`
- **无** ffmpeg/ffprobe 门控

## 环境变量与机器可读声明

- 环境变量键名与说明：**`manifest.yaml`**（`environment` 段）及本文
- 变量、凭据模型、合规 **`permissions`**、**`clientPermissions`、`agentPolicy`**：**`manifest.yaml`**

## 使用命令

- **ClawHub**（slug 以注册表为准）：`clawhub run chanjing-video-compose`
- **本仓库**：`python skills/chanjing-video-compose/scripts/create_task.py …`（见 **Standard Workflow**）

---

## 登记与审稿（单一事实来源）

凭据、`primaryEnv` 省略、可选 env、无 ffmpeg 门控（本 skill 独立使用场景）等：**以 `manifest.yaml` 为准**。本篇从 **When to Use** 起写流程与 API 说明。

## When to Use This Skill

当用户要做这些事时使用本 Skill：

* 创建数字人视频合成任务
* 用文本驱动数字人出镜
* 用本地音频驱动数字人视频
* 查询公共数字人或定制数字人形象
* 轮询视频合成结果
* 在用户明确要求时下载最终视频到本地

如果需求更接近“上传一段真人视频做对口型驱动”，优先使用 `chanjing-avatar`，不要混用。

## Preconditions

执行本 Skill 前，必须先通过 `chanjing-credentials-guard` 完成 AK/SK 与 Token 校验。

本 Skill 与 guard 共用：

* `~/.chanjing/credentials.json`
* `https://open-api.chanjing.cc`

无凭证时，脚本会自动打开蝉镜登录页，并提示配置命令。

### 审阅与安全（凭据与边界）

与 **Purpose / Credentials / Persistence** 相关的逐项说明见 **`manifest.yaml`**。以下仅 **SKILL 正文补充**：

- **`create_task.py --callback`**：若传入 URL，蝉镜可能向该端点推送任务结果；须自行评估信任与可达性。

## Standard Workflow

1. 先让用户明确选择数字人来源：`common`（公共数字人）或 `customised`（定制数字人）
2. 调用 `list_figures.py --source <common|customised>`（建议 `--json`，公共源可加大 `--page-size` 或翻页）获取可用形象；**在候选内对比** `name`、各 `figure` 的 `type` 与分辨率、`audio_man_id`、`audio_name`（若有）与任务人设后再选定 `person.id`。**禁止**未比较就默认列表最前几项。
3. 如果选择公共数字人，还要再确认 `figure_type`（与所选 `figures[].type` 一致），例如 `sit_body` / `whole_body` / `circle_view`。无用户特殊要求时，**默认优先年轻、有活力的形象**（名称/`audio_name` 偏青年、学生、元气等）；题材需要成熟或中老年气质时再改选。
4. 若使用文本驱动，确定 `audio_man_id`
5. 在创建任务前，必须明确询问用户字幕偏好：`show`（保留字幕）或 `hide`（隐藏字幕）
6. 如果用户选择 `show` 但没有提出自定义样式或位置需求，直接使用官方文档推荐默认值；只有在用户明确想调整字幕位置或样式时，才继续追问 `subtitle_config` 参数
7. 若用户要定制字幕位置，说明坐标以左上角为原点，再补充 `subtitle_config` 相关参数
8. 若使用本地音频或背景图，先调用 `upload_file.py` 获取 `file_id`
9. 调用 `create_task.py` 创建视频合成任务，得到 `video_id`
10. 调用 `poll_task.py` 轮询直到成功，得到 `video_url`
11. 只有在用户明确要求保存到本地时，才调用 `download_result.py`

## Covered APIs

本 Skill 当前覆盖：

* `GET /open/v1/list_common_dp`
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
| `list_figures.py` | 按 `--source common|customised` 列出数字人形象，输出 `person.id` / `figure_type` / `audio_man_id` / 预览信息 |
| `upload_file.py` | 上传音频或背景素材，轮询到文件可用后输出 `file_id` |
| `create_task.py` | 创建视频合成任务；使用公共数字人时可补充 `--figure-type ...`，字幕支持 `--subtitle show|hide` 以及完整字幕配置参数；可选 **`--callback`**（服务端可能向该 URL 推送结果） |
| `poll_task.py` | 轮询视频详情直到完成，默认输出 `video_url` |
| `download_result.py` | 下载最终视频到 `outputs/video-compose/` |

## Usage Examples

示例 1：公共数字人文本驱动

```bash
# 1. 先列公共数字人
python skills/chanjing-video-compose/scripts/list_figures.py --source common

# 2. 用公共数字人创建文本驱动视频
VIDEO_ID=$(python skills/chanjing-video-compose/scripts/create_task.py \
  --person-id "C-ef91f3a6db3144ffb5d6c581ff13c7ec" \
  --figure-type "sit_body" \
  --audio-man "C-0ae461135d8a4eb2b59c853162ea9848" \
  --subtitle "show" \
  --subtitle-x 31 \
  --subtitle-y 1521 \
  --subtitle-width 1000 \
  --subtitle-height 200 \
  --subtitle-font-size 64 \
  --subtitle-stroke-width 7 \
  --text "你好，这是一个蝉镜视频合成测试。")

# 3. 轮询到完成，拿到 video_url
python skills/chanjing-video-compose/scripts/poll_task.py --id "$VIDEO_ID"
```

示例 2：定制数字人上传本地音频驱动

```bash
python skills/chanjing-video-compose/scripts/list_figures.py --source customised

AUDIO_FILE_ID=$(python skills/chanjing-video-compose/scripts/upload_file.py \
  --service make_video_audio \
  --file ./input.wav)

VIDEO_ID=$(python skills/chanjing-video-compose/scripts/create_task.py \
  --person-id "C-ef91f3a6db3144ffb5d6c581ff13c7ec" \
  --subtitle "hide" \
  --audio-file-id "$AUDIO_FILE_ID")

python skills/chanjing-video-compose/scripts/poll_task.py --id "$VIDEO_ID"
```

示例 3：显式下载最终视频

```bash
python skills/chanjing-video-compose/scripts/download_result.py \
  --url "https://example.com/output.mp4"
```

## Download Rule

下载是显式动作，不是默认动作：

* `poll_task.py` 成功后应先返回 `video_url`
* 不要自动下载结果文件
* 只有当用户明确表达“下载到本地”“保存到 outputs”“帮我落盘”时，才执行 `download_result.py`

## Figure Selection Rule

选择数字人时遵循这条规则：

* 如果用户要用平台已有人物库，先走公共数字人：`list_figures.py --source common`
* 如果用户要用自己训练或上传生成的人物，先走定制数字人：`list_figures.py --source customised`
* 使用公共数字人创建视频时，可按所选形态传 `--figure-type <type>`
* 使用定制数字人时，不需要 `figure_type`

## Subtitle Rule

字幕遵循这条规则：

* 不要默认假设用户要字幕或不要字幕
* 创建任务前，必须先明确询问用户选择：`show` 或 `hide`
* 若由 **`chanjing-one-click-video-creation`** 的 **`run_render.py`** 调用 `create_task.py`，以当次 **`workflow.json` 根级 `subtitle_required`** 为准（**默认 false** → `--subtitle hide`；**true** → `show` 及推荐样式），**无需**为该一键成片路径再单独追问字幕开关，除非用户在需求里明确要求改字幕策略
* 用户选择保留字幕时，调用 `create_task.py --subtitle show`
* 若用户未指定字幕位置或样式，直接使用官方推荐默认值；`create_task.py` 在未传 `--subtitle-color` 时默认白字 `color=#FFFFFF`：1080p 为 `x=31 y=1521 width=1000 height=200 font_size=64 stroke_width=7 asr_type=0`；4K 画布为 `x=80 y=2840 width=2000 height=1000 font_size=150 stroke_width=7 asr_type=0`（两组均含 `color=#FFFFFF`）
* 用户选择隐藏字幕时，调用 `create_task.py --subtitle hide` 或兼容旧用法 `--hide-subtitle`
* 若用户要求调整字幕位置或样式，可继续传 `--subtitle-x` / `--subtitle-y` / `--subtitle-width` / `--subtitle-height` / `--subtitle-font-size` / `--subtitle-color` / `--subtitle-stroke-color` / `--subtitle-stroke-width` / `--subtitle-font-id` / `--subtitle-asr-type`
* 坐标基于左上角原点；字幕区域不能超出 `screen_width` / `screen_height`
* 如果用户只说“要字幕”但没指定位置，不必再追问具体数值；除非用户明确要调位置，否则直接走默认值

## Output Convention

默认本地输出目录：

* `outputs/video-compose/`

## Additional Resources

更多接口细节见：

* `skills/chanjing-video-compose/reference.md`
* `skills/chanjing-video-compose/examples.md`
