# Reference

## Covered APIs

本 skill 当前覆盖这些接口：

* `POST /open/v1/list_customised_person`
* `POST /open/v1/create_video`
* `GET /open/v1/video`
* `GET /open/v1/common/create_upload_url`
* `GET /open/v1/common/file_detail`

## Figure List Notes

接口：

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

* `person.id`: 形象 id，来自 `list_customised_person`
* `person.figure_type`: 公共数字人形态，如 `whole_body` / `sit_body`
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
* `callback`: 任务完成回调 URL

### Constraints and caveats

* 文本长度应小于 4000 字符
* 音频驱动目前适合 wav / mp3 / m4a；如需字幕，建议上传 8000 Hz 或 16000 Hz 单声道音频
* 背景图仅支持 `jpg` / `png`
* 开启 `resolution_rate=1` 时，最好先确认数字人 `support_4k=true`
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
| `list_figures` | `POST /open/v1/list_customised_person` |
| `upload_file` | `GET /open/v1/common/create_upload_url` + `PUT sign_url` + `GET /open/v1/common/file_detail` |
| `create_task` | `POST /open/v1/create_video` |
| `poll_task` | `GET /open/v1/video` |
| `download_result` | 下载 `video_url` 到本地 |

## Download Rule

* `download_result` 是显式动作，不应在 `poll_task` 成功后自动执行
* 优先先把 `video_url` 返回给用户
* 只有在用户确认下载时，才保存到 `outputs/video-compose/`
