# Reference

## Covered APIs

本 skill 当前覆盖这些接口：

* `POST /open/v1/ai_creation/task/submit`
* `POST /open/v1/ai_creation/task/page`
* `GET /open/v1/ai_creation/task`

## Why A Generic Submitter

蝉镜 AI 创作有很多图片/视频模型，但它们大都复用同一个提交端点：

```http
POST /open/v1/ai_creation/task/submit
```

不同模型主要差在请求体字段和 `model_code`，因此本 skill 采用：

* 一个通用 `submit_task`
* 一个通用 `get_task`
* 一个通用 `poll_task`

对常见字段做 CLI 参数映射，对模型私有字段保留 `--body-file` / `--body-json` 透传能力。

## Submit Task

接口：

```http
POST /open/v1/ai_creation/task/submit
```

这是异步任务接口，成功响应中的 `data` 即任务 `unique_id`。

### Common request fields

* `creation_type`: `3=图片生成`，`4=视频生成`
* `model_code`: 模型编码
* `ref_prompt`: 提示词
* `ref_img_url`: 参考图 URL 数组
* `aspect_ratio`: 比例，如 `1:1`、`3:4`、`4:3`、`9:16`、`16:9`
* `clarity`: 图片常见 `1024/2048/4096`，视频常见 `720/1080`
* `quality_mode`: 常见 `std` / `pro`
* `number_of_images`: 图片生成数量，1-4
* `video_duration`: 视频时长（秒）
* `style`: 部分视频模型支持的视频风格

### Typical image model example

以 `doubao-seedream-3.0-t2i` 为例：

```json
{
  "ref_prompt": "赛博朋克城市夜景，霓虹灯，雨夜，电影镜头",
  "creation_type": 3,
  "aspect_ratio": "16:9",
  "clarity": 2048,
  "number_of_images": 1,
  "model_code": "doubao-seedream-3.0-t2i"
}
```

注意：

* Seedream 3.0 不支持 `ref_img_url`

### Typical video model example

以 `tx_kling-v2-1-master` 为例：

```json
{
  "ref_img_url": [
    "https://res.chanjing.cc/chanjing/res/aigc_creation/photo/start.jpg",
    "https://res.chanjing.cc/chanjing/res/aigc_creation/photo/end.jpg"
  ],
  "ref_prompt": "角色从静止到转身，镜头平滑移动，叙事感强",
  "creation_type": 4,
  "aspect_ratio": "9:16",
  "clarity": 1080,
  "quality_mode": "pro",
  "video_duration": 5,
  "model_code": "tx_kling-v2-1-master"
}
```

### Other model notes

* `Doubao-Seedance-1.0-pro` 支持文生视频和图生视频
* `kling-v2-1` 图片模型文档页虽然列了 `ref_img_url`，但备注明确说不支持参考图

## Get Task

接口：

```http
GET /open/v1/ai_creation/task?unique_id=<unique_id>
```

返回字段与任务列表里的单条对象一致。重点关注：

* `unique_id`
* `type`: `3=图片`，`4=视频`
* `progress_desc`: `Queued / Ready / Generating / Success / Error`
* `err_msg`
* `output_url`
* `photo_info`
* `motion_info`
* `model_code`
* `model_name`

## List Tasks

接口：

```http
POST /open/v1/ai_creation/task/page
```

请求体关键字段：

* `unique_ids`: 任务 ID 列表，空数组表示不过滤
* `type`: `3=图片`，`4=视频`
* `page`
* `page_size`: 最大 50
* `is_success`: 是否只看成功任务

## Poll Termination Rules

本 skill 按 `progress_desc` 判断：

* `Queued` / `Ready` / `Generating`: 继续轮询
* `Success`: 成功，返回 `output_url`
* `Error` / `Fail`: 失败，停止并报错

## Output Fields

常见输出：

* 图片任务：`output_url` 为图片地址数组
* 视频任务：`output_url` 为视频地址数组

默认脚本行为：

* `poll_task` 默认输出第一条结果地址
* 使用 `--all-urls` 时输出完整 `output_url` 数组

## Common Status Codes

任务提交、详情、列表文档里常见状态码基本一致：

* `0`: 成功
* `400`: 参数格式错误
* `10400`: AccessToken 验证失败
* `40000`: 参数错误
* `40001`: 超出 QPS 限制
* `50000`: 系统内部错误

## Script Mapping

| 脚本 | 对应接口 |
|------|----------|
| `submit_task` | `POST /open/v1/ai_creation/task/submit` |
| `get_task` | `GET /open/v1/ai_creation/task` |
| `list_tasks` | `POST /open/v1/ai_creation/task/page` |
| `poll_task` | `GET /open/v1/ai_creation/task` |
| `download_result` | 下载 `output_url` 到本地 |

## Model Examples Referenced

本 skill 参考了这些模型页来整理通用字段：

* `doubao-seedream-3.0-t2i`
* `kling-v2-1`
* `tx_kling-v2-1-master`
* `Doubao-Seedance-1.0-pro`
