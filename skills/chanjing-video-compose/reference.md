# Reference

## Covered APIs

本 skill 当前覆盖这些接口：

* `GET /open/v1/list_common_dp`
* `POST /open/v1/list_customised_person`
* `POST /open/v1/create_video`
* `GET /open/v1/video`
* `GET /open/v1/common/create_upload_url`
* `GET /open/v1/common/file_detail`

## Figure List Notes

### 定制数字人接口

```http
POST /open/v1/list_customised_person
```

典型用途：

* 获取 `person.id`
* 获取默认可复用的 `audio_man_id`
* 查看是否支持 `support_4k`
* 获取 `preview_url` 便于人工选择形象

脚本默认关注这些字段：

* `id`
* `name`
* `audio_man_id`
* `support_4k`
* `preview_url`

### 公共数字人接口

```http
GET /open/v1/list_common_dp?page=<page>&size=<size>
```

典型用途：

* 获取公共数字人 `person.id`
* 获取该人物可用的 `figures[].type`
* 获取默认可复用的 `audio_man_id`
* 获取 `figures[].preview_video_url` 便于人工选择形象

脚本默认关注这些字段：

* `id`
* `name`
* `figures[].type`
* `figures[].width`
* `figures[].height`
* `audio_man_id`
* `audio_name`
* `figures[].preview_video_url`

## Create Task Notes

接口：

```http
POST /open/v1/create_video
```

这是异步任务接口，响应 `data` 即视频任务 id，需要继续调用详情接口轮询。

### Minimum body for TTS mode

```json
{
  "person": {
    "id": "C-figure-id",
    "x": 0,
    "y": 0,
    "width": 1080,
    "height": 1920
  },
  "audio": {
    "type": "tts",
    "volume": 100,
    "language": "cn",
    "tts": {
      "text": ["你好，这是一个测试。"],
      "speed": 1,
      "audio_man": "C-audio-man-id",
      "pitch": 1
    }
  },
  "bg_color": "#EDEDED",
  "screen_width": 1080,
  "screen_height": 1920
}
```

### Minimum body for audio mode

```json
{
  "person": {
    "id": "C-figure-id",
    "x": 0,
    "y": 0,
    "width": 1080,
    "height": 1920
  },
  "audio": {
    "type": "audio",
    "file_id": "uploaded-audio-file-id",
    "volume": 100,
    "language": "cn"
  },
  "bg_color": "#EDEDED",
  "screen_width": 1080,
  "screen_height": 1920
}
```

### Common request fields

* `person.id`: 形象 id，来自 `list_common_dp` 或 `list_customised_person`
* `person.figure_type`: 公共数字人形态，如 `whole_body` / `sit_body` / `circle_view`；使用公共数字人时必传
* `audio.type`: `tts` 或 `audio`
* `audio.tts.text`: 文本数组，建议把所有文本放进一个字符串
* `audio.tts.audio_man`: 声音 id，优先使用该形象返回的 `audio_man_id`
* `audio.file_id`: 本地上传音频的 file id
* `audio.wav_url`: 远端音频链接
* `bg.file_id`: 背景素材 file id
* `bg.src_url`: 背景图片地址
* `drive_mode`: `random` 表示随机帧动作；不传表示正常顺序驱动
* `backway`: 人物素材播放顺序，`1` 正放，`2` 倒放
* `is_rgba_mode`: 是否生成四通道 webm
* `model`: `0` 基础版，`1` 高质版
* `resolution_rate`: `0` 为 1080p，`1` 为 4K
* `subtitle_config.show`: 是否显示字幕
* `subtitle_config.x`: 字幕区域起始 x 坐标，默认推荐 `31`（4K 推荐 `80`）
* `subtitle_config.y`: 字幕区域起始 y 坐标，默认推荐 `1521`（4K 推荐 `2840`）
* `subtitle_config.width`: 字幕显示范围宽度，默认推荐 `1000`（4K 推荐 `2000`）
* `subtitle_config.height`: 字幕显示范围高度，默认推荐 `200`（4K 推荐 `1000`）
* `subtitle_config.font_size`: 字幕字号，默认推荐 `64`（4K 推荐 `150`）
* `subtitle_config.color`: 字幕颜色，格式 `#RRGGBB`
* `subtitle_config.stroke_color`: 字幕描边颜色，格式 `#RRGGBB`
* `subtitle_config.stroke_width`: 字幕描边宽度，推荐 `7`
* `subtitle_config.font_id`: 字幕字体 ID
* `subtitle_config.asr_type`: 字幕时间戳来源，`0` 自动生成，`1` 用户输入
* `callback`: 任务完成回调 URL

脚本约定：

* `create_task --subtitle show` 会传 `subtitle_config.show=true`
* 若未额外传字幕位置和样式参数，`create_task --subtitle show` 会自动补齐官方推荐默认值（含白字 `color=#FFFFFF`）：1080p 为 `31/1521/1000/200/64/#FFFFFF/7/0`，4K 画布为 `80/2840/2000/1000/150/#FFFFFF/7/0`
* `create_task --subtitle hide` 会传 `subtitle_config.show=false`
* `create_task --hide-subtitle` 兼容旧用法，也会传 `subtitle_config.show=false`
* `create_task` 支持通过 `--subtitle-x` / `--subtitle-y` / `--subtitle-width` / `--subtitle-height` / `--subtitle-font-size` / `--subtitle-color` / `--subtitle-stroke-color` / `--subtitle-stroke-width` / `--subtitle-font-id` / `--subtitle-asr-type` 覆盖默认字幕配置中的任意字段
* 若用户只确认“显示字幕”而未指定位置，代理应直接使用默认值；若用户要求“字幕更高一点”“靠左一点”等，再结合左上角原点规则追问具体坐标或给出建议值

### Constraints and caveats

* 文本长度应小于 4000 字符
* 音频驱动目前适合 wav / mp3 / m4a；如需字幕，建议上传 8000 Hz 或 16000 Hz 单声道音频
* 背景图仅支持 `jpg` / `png`
* 使用公共数字人时，先从 `figures[]` 中选定具体 `type`，再把对应的宽高映射到 `person.width` / `person.height`
* 开启 `resolution_rate=1` 时，最好先确认数字人 `support_4k=true`
* 字幕坐标以左上角为原点；若传 `subtitle_config.x/y/width/height`，应确保字幕区域不超出屏幕范围
* 下载不应由创建或轮询脚本自动触发

## Poll Detail Notes

接口：

```http
GET /open/v1/video?id=<video_id>
```

轮询关注字段：

* `id`
* `status`
* `progress`
* `msg`
* `video_url`
* `subtitle_data_url`
* `preview_url`
* `duration`

状态流转：

* `10`: 生成中，继续轮询
* `30`: 成功，返回 `video_url`
* `4X`: 参数异常，视为失败
* `5X`: 服务异常，视为失败

## File Upload Notes

接口流程：

1. `GET /open/v1/common/create_upload_url?service=<service>&name=<filename>`
2. 用返回的 `sign_url` 执行 `PUT`
3. `GET /open/v1/common/file_detail?id=<file_id>` 直到文件可用

视频合成常用 `service`：

* `make_video_audio`
* `make_video_background`

文件就绪状态：

* `status = 1`: 文件可用

失败状态：

* `status = 98`: 内容安全检测失败
* `status = 99`: 文件标记删除
* `status = 100`: 文件已清理

## Script Mapping

| 脚本 | 对应接口 |
|------|----------|
| `list_figures` | `GET /open/v1/list_common_dp` 或 `POST /open/v1/list_customised_person` |
| `upload_file` | `GET /open/v1/common/create_upload_url` + `PUT sign_url` + `GET /open/v1/common/file_detail` |
| `create_task` | `POST /open/v1/create_video` |
| `poll_task` | `GET /open/v1/video` |
| `download_result` | 下载 `video_url` 到本地 |

## Download Rule

* `download_result` 是显式动作，不应在 `poll_task` 成功后自动执行
* 优先先把 `video_url` 返回给用户
* 只有在用户确认下载时，才保存到 `outputs/video-compose/`
