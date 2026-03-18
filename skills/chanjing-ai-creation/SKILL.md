---
name: chanjing-ai-creation
description: Use Chanjing AI creation APIs to submit image or video generation tasks across multiple models, inspect task status, poll async results, and explicitly download generated assets when requested.
---

# Chanjing AI Creation

## When to Use This Skill

当用户要做这些事时使用本 Skill：

* 用蝉镜 AI 创作模型生成图片
* 用蝉镜 AI 创作模型生成视频
* 查询 AI 创作任务列表或单个任务详情
* 轮询 AI 创作异步结果
* 在用户明确要求时下载图片或视频到本地

如果需求更接近“文生数字人”，优先使用 `chanjing-text-to-digital-person`。  
如果需求更接近“已有数字人视频合成”，优先使用 `chanjing-video-compose`。

## Preconditions

执行本 Skill 前，必须先通过 `chanjing-credentials-guard` 完成 AK/SK 与 Token 校验。

本 Skill 与 guard 共用：

* `~/.chanjing/credentials.json`
* `https://open-api.chanjing.cc`

无凭证时，脚本会自动打开蝉镜登录页，并提示配置命令。

## Standard Workflow

AI 创作的主接口是统一提交器：

1. 调用 `submit_task` 提交图片或视频生成任务，得到 `unique_id`
2. 调用 `poll_task` 轮询直到成功，得到 `output_url`
3. 如需回看任务参数或错误原因，调用 `get_task`
4. 如需看历史记录，调用 `list_tasks`
5. 只有在用户明确要求保存到本地时，才调用 `download_result`

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
| `_auth.py` | 读取凭证、获取或刷新 `access_token` |
| `submit_task` | 提交 AI 创作任务，输出 `unique_id` |
| `get_task` | 获取单个任务详情 |
| `list_tasks` | 列出图片或视频任务 |
| `poll_task` | 轮询任务直到完成，默认输出第一个结果地址 |
| `download_result` | 下载图片或视频到 `outputs/ai-creation/` |

## Usage Examples

示例 1：Seedream 3.0 文生图

```bash
TASK_ID=$(python3 skills/chanjing-ai-creation/scripts/submit_task \
  --creation-type 3 \
  --model-code "doubao-seedream-3.0-t2i" \
  --prompt "赛博朋克城市夜景，霓虹灯，雨夜，电影镜头" \
  --aspect-ratio "16:9" \
  --clarity 2048 \
  --number-of-images 1)

python3 skills/chanjing-ai-creation/scripts/poll_task --unique-id "$TASK_ID"
```

示例 2：腾讯 Kling v2.1 Master 图生视频

```bash
TASK_ID=$(python3 skills/chanjing-ai-creation/scripts/submit_task \
  --creation-type 4 \
  --model-code "tx_kling-v2-1-master" \
  --ref-img-url "https://res.chanjing.cc/chanjing/res/aigc_creation/photo/start.jpg" \
  --ref-img-url "https://res.chanjing.cc/chanjing/res/aigc_creation/photo/end.jpg" \
  --prompt "角色从静止到转身，镜头平滑移动，叙事感强" \
  --aspect-ratio "9:16" \
  --clarity 1080 \
  --quality-mode pro \
  --video-duration 5)

python3 skills/chanjing-ai-creation/scripts/poll_task --unique-id "$TASK_ID"
```

示例 3：直接透传完整 JSON

```bash
python3 skills/chanjing-ai-creation/scripts/submit_task \
  --body-file ./payload.json
```

## Download Rule

下载是显式动作，不是默认动作：

* `poll_task` 成功后应先返回远端 `output_url`
* 不要自动下载结果文件
* 只有当用户明确表达“下载到本地”“保存到 outputs”“帮我落盘”时，才执行 `download_result`

## Output Convention

默认本地输出目录：

* `outputs/ai-creation/`

## Additional Resources

更多接口细节见：

* `skills/chanjing-ai-creation/reference.md`
* `skills/chanjing-ai-creation/examples.md`
