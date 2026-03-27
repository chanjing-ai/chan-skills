# Examples

## Natural Language Triggers

这些说法通常应该触发本 skill：

* “帮我生成一个文生数字人形象”
* “根据这些提示词先出一张数字人图”
* “把这张文生图转成会说话的视频”
* “帮我查一下文生数字人任务状态”
* “把生成好的图片或视频下载到本地”
* “帮我跑一个 LoRA 训练任务”

## Minimal CLI Flows

### 1. 文生图 -> 图生视频

```bash
PHOTO_TASK_ID=$(python3 skills/chanjing-text-to-digital-person/scripts/create_photo_task.py \
  --age "Young adult" \
  --gender Female \
  --number-of-images 1 \
  --industry "知识分享" \
  --background "简洁演播室背景" \
  --detail "干练短发，职业装，镜头感强" \
  --talking-pose "上半身特写，站立讲解")

PHOTO_URL=$(python3 skills/chanjing-text-to-digital-person/scripts/poll_photo_task.py \
  --unique-id "$PHOTO_TASK_ID")

MOTION_TASK_ID=$(python3 skills/chanjing-text-to-digital-person/scripts/create_motion_task.py \
  --photo-unique-id "$PHOTO_TASK_ID" \
  --photo-path "$PHOTO_URL" \
  --emotion "自然播报，语气温和自信" \
  --gesture)

python3 skills/chanjing-text-to-digital-person/scripts/poll_motion_task.py \
  --unique-id "$MOTION_TASK_ID"
```

### 2. 查看任务列表

```bash
python3 skills/chanjing-text-to-digital-person/scripts/list_tasks.py
```

### 3. LoRA 训练

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

### 4. 显式下载

```bash
python3 skills/chanjing-text-to-digital-person/scripts/download_result.py \
  --url "https://example.com/output.mp4"
```

## Expected Outputs

* `create_photo_task.py` 输出 `photo_unique_id`
* `poll_photo_task.py` 默认输出第一张图片地址
* `create_motion_task.py` 输出 `motion_unique_id`
* `poll_motion_task.py` 默认输出视频地址
* `create_lora_task.py` 输出 `lora_id`
* `poll_lora_task.py` 默认输出第一条 `photo_task_id`
* `download_result.py` 输出本地文件路径
