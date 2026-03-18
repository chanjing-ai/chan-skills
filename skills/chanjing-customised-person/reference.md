# Reference

## Covered APIs

本 skill 当前覆盖这些接口：

* `GET /open/v1/common/create_upload_url`
* `GET /open/v1/common/file_detail`
* `POST /open/v1/create_customised_person`
* `POST /open/v1/list_customised_person`
* `GET /open/v1/customised_person`
* `POST /open/v1/delete_customised_person`

## File Upload Notes

接口流程：

1. `GET /open/v1/common/create_upload_url?service=customised_person&name=<filename>`
2. 用返回的 `sign_url` 执行 `PUT`
3. `GET /open/v1/common/file_detail?id=<file_id>` 直到文件可用

本 skill 默认使用：

* `service=customised_person`

文件状态重点关注：

* `status = 1`: 文件可用
* `status = 0`: 文件尚未就绪，继续轮询
* `status = 98`: 内容安全检测失败
* `status = 99`: 文件被标记删除
* `status = 100`: 文件已被彻底清理

注意事项：

* 上传地址 15 分钟内有效
* 文件最多可能需要约 1 分钟才能可用
* 超过 30 天的文件会被自动删除

## Create Customised Person Notes

接口：

```http
POST /open/v1/create_customised_person
```

这是异步接口，响应中的 `data` 直接返回 `person_id`，后续需要继续查询详情接口确认制作结果。

### Minimum body

```json
{
  "name": "open_api_测试",
  "file_id": "e284db4d95de4220afe78132158156b5",
  "train_type": "figure",
  "error_skip": false,
  "resolution_rate": 0
}
```

### Common request fields

* `name`: 定制数字人名称
* `file_id`: 来自文件管理的素材文件 id
* `callback`: 任务结束后的回调地址，回调体与详情接口 `data` 结构相同
* `train_type`: 训练类型。参数表里明确写了 `figure`生成的数字人只包含形象不定制声音；`both`即定制数字人也会创建声音，未确认时建议使用 `both`
* `language`: 需生成声音时可传，当前文档说明支持 `cn` / `en`
* `error_skip`: 是否跳过部分失败，当前主要用于跳过声音克隆失败
* `resolution_rate`: `0=1080p`，`1=4K`

### Constraints and caveats

* 源视频格式应为 `mp4`、`mov` 或 `webm`
* 源视频时长上限 5 分钟
* 若设置 `resolution_rate=1`，建议上传 4K 视频素材
* 文档说明该接口 QPS 限制为 10/min

### Status codes

重点响应码：

* `0`: 成功
* `10400`: AccessToken 校验失败
* `40000`: 参数错误
* `40001`: 超出 QPS 限制
* `40002`: 定制数字人数量到达上限
* `50000` / `51000`: 系统内部错误

## List Notes

接口：

```http
POST /open/v1/list_customised_person
```

脚本默认关注这些字段：

* `id`
* `name`
* `status`
* `progress`
* `audio_man_id`
* `support_4k`
* `preview_url`

状态含义：

* `1`: 制作中
* `2`: 成功
* `4`: 失败
* `5`: 系统错误

## Detail Notes

接口：

```http
GET /open/v1/customised_person?id=<person_id>
```

详情接口是本 skill 的核心轮询接口，可返回：

* `id`
* `name`
* `pic_url`
* `preview_url`
* `audio_man_id`
* `status`
* `err_reason`
* `reason`
* `progress`
* `create_time`
* `support_4k`
* `height_4k`
* `width_4k`

### Poll termination rules

* `status = 1`: 继续轮询
* `status = 2`: 成功，视为形象可用
* `status = 4` 或 `5`: 失败，停止并报错

成功后常用输出：

* `preview_url`: 预览视频地址
* `pic_url`: 封面图地址
* `audio_man_id`: 若成功生成声音，可用于后续视频合成

## Delete Notes

接口：

```http
POST /open/v1/delete_customised_person
```

最小请求体：

```json
{
  "id": "C-ef91f3a6db3144ffb5d6c581ff13c7ec"
}
```

删除成功时响应只返回通用成功消息，因此脚本直接回显传入的 `person_id`。

## Script Mapping

| 脚本 | 对应接口 |
|------|----------|
| `get_upload_url` | `GET /open/v1/common/create_upload_url` |
| `upload_file` | `GET /open/v1/common/create_upload_url` + `PUT sign_url` + `GET /open/v1/common/file_detail` |
| `create_person` | `POST /open/v1/create_customised_person` |
| `list_persons` | `POST /open/v1/list_customised_person` |
| `get_person` | `GET /open/v1/customised_person` |
| `poll_person` | `GET /open/v1/customised_person` |
| `delete_person` | `POST /open/v1/delete_customised_person` |
