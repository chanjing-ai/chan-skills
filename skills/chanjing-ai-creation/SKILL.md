---
name: chanjing-ai-creation
description: >-
  Chanjing AI creation Open API client: submit image/video tasks, poll task
  status, list and get tasks, and optionally download outputs when the user runs
  download_result.py. Reads and writes local credentials.json; calls
  open-api.chanjing.cc.
credential: credentials.json (read/write app_id, secret_key, access_token on disk)
openclaw_primary_env: false
environment: CHANJING_OPENAPI_CREDENTIALS_DIR, CHANJING_OPENAPI_BASE_URL
legacy_environment: CHANJING_CONFIG_DIR, CHANJING_API_BASE
machine_readable: manifest.yaml
requires_ffmpeg: false
requires_ffprobe: false
---

# Chanjing AI Creation

## 功能说明

调用蝉镜 **AI 创作** Open API：**提交任务**、**轮询状态**、**列表与单条查询**；仅在用户明确要求时用 `download_result.py` **可选下载**输出。需**读写**本地 `credentials.json` 并访问 Open API。跨模型文生图/视频等由 `submit_task.py` 参数与透传体决定。本 skill 脚本**不**依赖 ffmpeg/ffprobe。

## 运行依赖

- **python3** 与同仓库 `scripts/*.py`
- **无** ffmpeg/ffprobe 门控

## 环境变量与机器可读声明

- 环境变量键名与说明：**`manifest.yaml`**（`environment` 段）及本文
- 变量、凭据、合规 **`permissions`**、**`clientPermissions`、`agentPolicy`**：**`manifest.yaml`**

## 使用命令

- **ClawHub**（slug 以注册表为准）：`clawhub run chanjing-ai-creation`
- **本仓库示例**：`python skills/chanjing-ai-creation/scripts/submit_task.py …`（见正文 **Standard Workflow**）

---

## 登记与审稿（单一事实来源）

主凭据、可选 env、下载信任边界等：**以 `manifest.yaml` 为准**。本篇从 **When to Use** 起写业务能力。

## When to Use This Skill

当用户要做这些事时使用本 Skill：

* **提交**图片或视频 AI 创作任务（`submit_task.py`）
* **列表 / 单条查询**任务（`list_tasks.py`、`get_task.py`）
* **轮询**异步结果直至完成（`poll_task.py`）
* 仅在用户明确要求时**下载**输出（`download_result.py`）

上述流程依赖读写本地 `credentials.json` 并调用 `open-api.chanjing.cc`。

如果需求更接近“文生数字人”，优先使用 `chanjing-text-to-digital-person`。  
如果需求更接近“已有数字人视频合成”，优先使用 `chanjing-video-compose`。

## Preconditions

执行本 Skill 前，必须先通过 `chanjing-credentials-guard` 完成 AK/SK 与 Token 校验。

本 Skill 与 guard 共用：

* `~/.chanjing/credentials.json`
* `https://open-api.chanjing.cc`

无凭证时，脚本会自动打开蝉镜登录页，并提示配置命令。

### 审阅与安全（凭据）

与 **Purpose / Credentials / Persistence**、**`download_result.py`** 信任边界相关的逐项说明见 **`manifest.yaml`**。

**运行时范围**：本 Skill 的说明与脚本仅服务于已声明用途——读取本地 **`credentials.json`**、调用蝉镜 **Open API** 端点；**不**在轮询或查询成功时自动落盘生成物，**仅**在用户显式执行 **`download_result.py`** 时下载资源。

**`_auth.py` 与仓库布局**：鉴权辅助可能打开系统浏览器，或按相对路径调用同仓库下的 **`chanjing-credentials-guard`** 脚本（例如 `open_login_page.py`）。这假设当前工作区为 **chan-skills 式多 Skill 目录结构**，或已单独安装并具备等效路径的 guard skill；否则将回退为仅打开登录页 URL。

**敏感数据与持久化**：预期仅处理 **`credentials.json`** 中的 `app_id`、`secret_key`、`access_token`（及与 token 生命周期相关的字段，见 `manifest.yaml`）。将 **`access_token` 写入磁盘** 是有意设计且已文档化，对 API 客户端而言通常可接受；但在**多人共用主机**、**全盘备份/同步到不可信存储**等场景下，磁盘上的 token 会**扩大泄露面**，需按环境自行评估。

## Standard Workflow

AI 创作的主接口是统一提交器：

1. 调用 `submit_task.py` 提交图片或视频生成任务，得到 `unique_id`
2. 调用 `poll_task.py` 轮询直到成功，得到 `output_url`
3. 如需回看任务参数或错误原因，调用 `get_task.py`
4. 如需看历史记录，调用 `list_tasks.py`
5. 只有在用户明确要求保存到本地时，才调用 `download_result.py`

这个 skill 默认做成“通用任务提交器”：

* 对常见图片/视频模型，优先使用脚本提供的通用参数
* 对特殊模型参数，使用 `--body-file` 或 `--body-json` 透传完整请求体

## Covered APIs

本 Skill 当前覆盖：

* `POST /open/v1/ai_creation/task/submit`
* `POST /open/v1/ai_creation/task/page`
* `GET /open/v1/ai_creation/task`

## Scripts

脚本目录：

* `skills/chanjing-ai-creation/scripts/`

| 脚本 | 说明 |
|------|------|
| `_auth.py` | 读写 `credentials.json`、获取或刷新 `access_token` |
| `submit_task.py` | 提交 AI 创作任务，输出 `unique_id` |
| `get_task.py` | 获取单个任务详情 |
| `list_tasks.py` | 列出图片或视频任务 |
| `poll_task.py` | 轮询任务直到完成，默认输出第一个结果地址 |
| `download_result.py` | 下载图片或视频到 `outputs/ai-creation/` |

## Usage Examples

示例 1：Seedream 3.0 文生图

```bash
TASK_ID=$(python3 skills/chanjing-ai-creation/scripts/submit_task.py \
  --creation-type 3 \
  --model-code "doubao-seedream-3.0-t2i" \
  --prompt "赛博朋克城市夜景，霓虹灯，雨夜，电影镜头" \
  --aspect-ratio "16:9" \
  --clarity 2048 \
  --number-of-images 1)

python3 skills/chanjing-ai-creation/scripts/poll_task.py --unique-id "$TASK_ID"
```

示例 2：腾讯 Kling v2.1 Master 图生视频

```bash
TASK_ID=$(python3 skills/chanjing-ai-creation/scripts/submit_task.py \
  --creation-type 4 \
  --model-code "tx_kling-v2-1-master" \
  --ref-img-url "https://res.chanjing.cc/chanjing/res/aigc_creation/photo/start.jpg" \
  --ref-img-url "https://res.chanjing.cc/chanjing/res/aigc_creation/photo/end.jpg" \
  --prompt "角色从静止到转身，镜头平滑移动，叙事感强" \
  --aspect-ratio "9:16" \
  --clarity 1080 \
  --quality-mode pro \
  --video-duration 5)

python3 skills/chanjing-ai-creation/scripts/poll_task.py --unique-id "$TASK_ID"
```

示例 3：直接透传完整 JSON

```bash
python3 skills/chanjing-ai-creation/scripts/submit_task.py \
  --body-file ./payload.json
```

## Download Rule

下载是显式动作，不是默认动作：

* `poll_task.py` 成功后应先返回远端 `output_url`
* 不要自动下载结果文件
* 只有当用户明确表达“下载到本地”“保存到 outputs”“帮我落盘”时，才执行 `download_result.py`

## Output Convention

默认本地输出目录：

* `outputs/ai-creation/`

## Additional Resources

更多接口细节见：

* `skills/chanjing-ai-creation/reference.md`
* `skills/chanjing-ai-creation/examples.md`
