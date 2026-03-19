# Examples

## Natural Language Triggers

这些说法通常应该触发本 skill：

* “帮我做一个蝉镜数字人视频”
* “用这段文案生成一个数字人口播视频”
* “先列一下公共数字人”
* “先列一下我自己的定制数字人”
* “把这段 wav 上传后做成数字人视频”
* “帮我轮询视频合成任务状态”
* “把生成好的视频下载到本地”

## Minimal CLI Flows

### 1. 公共数字人文本驱动

```bash
python skills/chanjing-video-compose/scripts/list_figures --source common

VIDEO_ID=$(python skills/chanjing-video-compose/scripts/create_task \
  --person-id "C-ef91f3a6db3144ffb5d6c581ff13c7ec" \
  --figure-type "sit_body" \
  --audio-man "C-0ae461135d8a4eb2b59c853162ea9848" \
  --subtitle "show" \
  --text "你好，这是一个蝉镜视频合成测试。")

python skills/chanjing-video-compose/scripts/poll_task --id "$VIDEO_ID"
```

说明：

* 仅传 `--subtitle show` 时，脚本会自动补官方推荐字幕参数
* 如需自定义位置或样式，再继续补充 `--subtitle-x` / `--subtitle-y` / `--subtitle-width` / `--subtitle-height` / `--subtitle-font-size` 等参数

### 2. 公共数字人文本驱动，自定义字幕位置

```bash
VIDEO_ID=$(python skills/chanjing-video-compose/scripts/create_task \
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

python skills/chanjing-video-compose/scripts/poll_task --id "$VIDEO_ID"
```

### 3. 定制数字人本地音频驱动

```bash
python skills/chanjing-video-compose/scripts/list_figures --source customised

AUDIO_FILE_ID=$(python skills/chanjing-video-compose/scripts/upload_file \
  --service make_video_audio \
  --file ./demo.wav)

VIDEO_ID=$(python skills/chanjing-video-compose/scripts/create_task \
  --person-id "C-ef91f3a6db3144ffb5d6c581ff13c7ec" \
  --audio-file-id "$AUDIO_FILE_ID")

python skills/chanjing-video-compose/scripts/poll_task --id "$VIDEO_ID"
```

### 4. 带背景图

```bash
BG_FILE_ID=$(python skills/chanjing-video-compose/scripts/upload_file \
  --service make_video_background \
  --file ./background.png)

VIDEO_ID=$(python skills/chanjing-video-compose/scripts/create_task \
  --person-id "C-ef91f3a6db3144ffb5d6c581ff13c7ec" \
  --figure-type "whole_body" \
  --audio-man "C-0ae461135d8a4eb2b59c853162ea9848" \
  --text "欢迎来到我的频道。" \
  --bg-file-id "$BG_FILE_ID")
```

### 5. 显式下载

```bash
python skills/chanjing-video-compose/scripts/download_result \
  --url "https://example.com/output.mp4"
```

## Expected Outputs

* `list_figures` 默认输出表格，便于挑选 `person.id`，公共数字人还会显示 `figure_type`
* `upload_file` 输出 `file_id`
* `create_task` 输出 `video_id`
* `poll_task` 默认输出 `video_url`
* `download_result` 输出本地文件路径
