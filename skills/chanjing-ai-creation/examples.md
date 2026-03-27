# Examples

## Natural Language Triggers

这些说法通常应该触发本 skill：

* “用 Seedream 帮我生成一张海报图”
* “用 Kling 做一个图生视频”
* “帮我提交一个 AI 创作视频任务”
* “查一下这个 AI 创作任务现在到哪了”
* “把刚生成的图片下载到本地”
* “我有完整 payload.json，帮我直接提交”

## Minimal CLI Flows

### 1. Seedream 3.0 文生图

```bash
TASK_ID=$(python3 skills/chanjing-ai-creation/scripts/submit_task.py \
  --creation-type 3 \
  --model-code "doubao-seedream-3.0-t2i" \
  --prompt "赛博朋克城市夜景，霓虹灯，雨夜，电影镜头" \
  --aspect-ratio "16:9" \
  --clarity 2048 \
  --number-of-images 1)

python3 skills/chanjing-ai-creation/scripts/poll_task.py \
  --unique-id "$TASK_ID"
```

### 2. 腾讯 Kling v2.1 Master 图生视频

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

python3 skills/chanjing-ai-creation/scripts/poll_task.py \
  --unique-id "$TASK_ID"
```

### 3. 直接透传完整 JSON

```bash
python3 skills/chanjing-ai-creation/scripts/submit_task.py \
  --body-file ./payload.json
```

### 4. 查看历史任务

```bash
python3 skills/chanjing-ai-creation/scripts/list_tasks.py --type 3
python3 skills/chanjing-ai-creation/scripts/list_tasks.py --type 4 --success-only
```

### 5. 显式下载

```bash
python3 skills/chanjing-ai-creation/scripts/download_result.py \
  --url "https://example.com/output.png"
```

## Expected Outputs

* `submit_task.py` 输出任务 `unique_id`
* `poll_task.py` 默认输出第一个结果 URL
* `get_task.py` 默认输出任务详情 JSON
* `list_tasks.py` 默认输出摘要行
* `download_result.py` 输出本地文件路径
