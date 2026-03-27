---
name: chanjing-text-to-digital-person
description: >-
  Use Chanjing text-to-digital-person APIs for AI portraits, talking videos,
  optional LoRA training, polling, and explicit downloads when requested.
credential: credentials.json (app_id/secret_key; access_token persisted on disk)
openclaw_primary_env: false
environment: CHANJING_OPENAPI_CREDENTIALS_DIR, CHANJING_OPENAPI_BASE_URL
legacy_environment: CHANJING_CONFIG_DIR, CHANJING_API_BASE
machine_readable: manifest.yaml
requires_ffmpeg: false
requires_ffprobe: false
notes: May invoke chanjing-credentials-guard open_login_page.py when AK/SK missing.
---

# Chanjing Text To Digital Person

## 功能说明

文生图、图生说话视频、可选 **LoRA** 训练与轮询；用户明确要求时下载生成物。凭据与权限见 **`manifest.yaml`**。脚本**不**依赖 ffmpeg/ffprobe。

## 运行依赖

- **python3** 与同仓库 `scripts/*.py`（含 `_auth.py`、`_task_api.py`）
- **无** ffmpeg/ffprobe 门控

## 环境变量与机器可读声明

- 环境变量键名与说明：**`manifest.yaml`**（`environment` 段）及本文
- 变量、凭据模型、合规 **`permissions`**、**`clientPermissions`、`agentPolicy`**：**`manifest.yaml`**

## 使用命令

- **ClawHub**（slug 以注册表为准）：`clawhub run chanjing-text-to-digital-person`
- **本仓库**：`python skills/chanjing-text-to-digital-person/scripts/create_photo_task.py …`（见 **Standard Workflow**）

---

## 登记与审稿（单一事实来源）

路径、`primaryEnv` 省略、**`persistAccessTokenOnDisk`**、敏感字段、**`agentPolicy`**、可选 env 等：**以 `manifest.yaml` 为准**。实现上由 **`_auth.py`**、**`_task_api.py`** 与各 CLI 脚本承担；本篇从 **When to Use** 起写流程。

## When to Use This Skill

当用户要做这些事时使用本 Skill：

* 根据人物提示词生成数字人形象图
* 把生成的人物图转成会说话的短视频
* 查询文生图 / 图生视频 / LoRA 任务状态
* 在用户明确要求时，把生成图片或视频下载到本地

如果需求是“上传真人素材训练定制数字人”，优先使用 `chanjing-customised-person`。  
如果需求是“拿已有数字人做口播视频合成”，优先使用 `chanjing-video-compose`。

## Preconditions

执行本 Skill 前，必须先通过 `chanjing-credentials-guard` 完成 AK/SK 与 Token 校验。

本 Skill 与 guard 共用：

* `~/.chanjing/credentials.json`
* `https://open-api.chanjing.cc`

无凭证时，脚本会自动打开蝉镜登录页（若同仓库存在则执行 **`chanjing-credentials-guard/scripts/open_login_page.py`**，否则 **`webbrowser.open`**），并提示本地执行 **`chanjing_config.py`**。

### 审阅与安全（凭据）

与 **Purpose / Credentials / Persistence** 相关的逐项说明见 **`manifest.yaml`**（缺凭证时可能子进程调用 guard 的 **`open_login_page.py`** 等行为见 **`clientPermissions`**）。

## Standard Workflow

主流程通常分两段，且都是异步任务：

1. 调用 `create_photo_task.py` 创建文生图任务，得到 `photo_unique_id`
2. 调用 `poll_photo_task.py` 轮询到成功，选一张 `photo_path`
3. 调用 `create_motion_task.py` 创建图生视频任务，得到 `motion_unique_id`
4. 调用 `poll_motion_task.py` 轮询到成功，得到最终 `video_url`
5. 只有在用户明确要求保存到本地时，才调用 `download_result.py`

可选扩展：

* 若用户想做 LoRA 训练，调用 `create_lora_task.py` 和 `poll_lora_task.py`
* `poll_lora_task.py` 成功后会返回一条 `photo_task_id`，可继续用 `poll_photo_task.py` 拿图

## Covered APIs

本 Skill 当前覆盖：

* `POST /open/v1/aigc/photo`
* `GET /open/v1/aigc/photo/task`
* `GET /open/v1/aigc/photo/task/page`
* `POST /open/v1/aigc/motion`
* `GET /open/v1/aigc/motion/task`
* `POST /open/v1/aigc/lora/task/create`
* `GET /open/v1/aigc/lora/task`

## Scripts

脚本目录：

* `skills/chanjing-text-to-digital-person/scripts/`

### 本仓库随附文件（勿与仅含 `_auth.py` 的精简包混淆）

完整包内含 **`_auth.py`**、**`_task_api.py`**（供任务脚本复用）及下列 **`.py` CLI**；请用 **`python3 <路径>/<脚本名>.py`** 调用（与仓库内其它蝉镜 skill 约定一致）。

| 文件名（仓库内） | 说明 |
|------------------|------|
| `_auth.py` | 读 **`credentials.json`**、刷新并 **写回** **`access_token` / `expire_in`**；缺 AK/SK 时尝试 **`open_login_page.py`** |
| `_task_api.py` | 任务 API 共用逻辑（由各 CLI import） |
| `create_photo_task.py` | 创建文生图任务 → `photo_unique_id` |
| `get_photo_task.py` | 单个文生图任务详情 |
| `list_tasks.py` | 任务列表（`type=1` photo，`type=2` motion） |
| `poll_photo_task.py` | 轮询文生图至完成 → 默认首张图 URL |
| `create_motion_task.py` | 创建图生视频 → `motion_unique_id` |
| `get_motion_task.py` | 单个图生视频任务详情 |
| `poll_motion_task.py` | 轮询图生视频至完成 → 默认视频 URL |
| `create_lora_task.py` | 创建 LoRA 训练 → `lora_id` |
| `get_lora_task.py` | LoRA 任务详情 |
| `poll_lora_task.py` | 轮询 LoRA 至完成 → 默认首条 `photo_task_id` |
| `download_result.py` | 仅在需要落盘时：下载到 `outputs/text-to-digital-person/`（或 `--output`） |

若环境中 **缺少** 上表任一入口或 **`_task_api.py`**，属于 **分发/打包不完整**。

## Usage Examples

示例 1：文生图后直接图生视频

```bash
PHOTO_TASK_ID=$(python3 skills/chanjing-text-to-digital-person/scripts/create_photo_task.py \
  --age "Young adult" \
  --gender Female \
  --number-of-images 1 \
  --industry "教育培训" \
  --background "现代直播间背景" \
  --detail "短发，亲和力强，职业装" \
  --talking-pose "上半身特写，站立讲解")

PHOTO_URL=$(python3 skills/chanjing-text-to-digital-person/scripts/poll_photo_task.py \
  --unique-id "$PHOTO_TASK_ID")

MOTION_TASK_ID=$(python3 skills/chanjing-text-to-digital-person/scripts/create_motion_task.py \
  --photo-unique-id "$PHOTO_TASK_ID" \
  --photo-path "$PHOTO_URL" \
  --emotion "自然播报，语气清晰自信" \
  --gesture)

python3 skills/chanjing-text-to-digital-person/scripts/poll_motion_task.py \
  --unique-id "$MOTION_TASK_ID"
```

示例 2：LoRA 训练

```bash
LORA_ID=$(python3 skills/chanjing-text-to-digital-person/scripts/create_lora_task.py \
  --name "演示LoRA" \
  --photo-url https://example.com/1.jpg \
  --photo-url https://example.com/2.jpg \
  --photo-url https://example.com/3.jpg \
  --photo-url https://example.com/4.jpg \
  --photo-url https://example.com/5.jpg)

python3 skills/chanjing-text-to-digital-person/scripts/poll_lora_task.py \
  --lora-id "$LORA_ID"
```

## Download Rule

下载是显式动作，不是默认动作：

* `poll_photo_task.py` 和 `poll_motion_task.py` 成功后应先返回远端 URL
* 不要自动下载结果文件
* 只有当用户明确表达“下载到本地”“保存到 outputs”“帮我落盘”时，才执行 `download_result.py`

## Output Convention

默认本地输出目录：

* `outputs/text-to-digital-person/`

## Additional Resources

更多接口细节见：

* `skills/chanjing-text-to-digital-person/reference.md`
* `skills/chanjing-text-to-digital-person/examples.md`
