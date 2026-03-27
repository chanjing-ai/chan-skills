# Reference

## Covered APIs

本 skill 当前覆盖这些接口：

* `POST /open/v1/aigc/photo`
* `GET /open/v1/aigc/photo/task`
* `GET /open/v1/aigc/photo/task/page`
* `POST /open/v1/aigc/motion`
* `GET /open/v1/aigc/motion/task`
* `POST /open/v1/aigc/lora/task/create`
* `GET /open/v1/aigc/lora/task`

## Workflow Notes

“文生数字人”在当前开放接口里更适合理解为两阶段工作流：

1. 先通过 `POST /open/v1/aigc/photo` 生成人物图
2. 再通过 `POST /open/v1/aigc/motion` 把人物图转成会说话的视频

两段都是异步任务，必须轮询详情接口直到成功。

LoRA 是可选增强流程：

1. `POST /open/v1/aigc/lora/task/create`
2. `GET /open/v1/aigc/lora/task`
3. 成功后拿到 `photo_task_ids`，再去查 photo 任务结果

## Create Photo Task

接口：

```http
POST /open/v1/aigc/photo
```

这是异步任务接口，响应 `data` 即文生图任务 `unique_id`。

### Required fields

* `age`: 年龄提示词，示例 `Young adult`
* `gender`: `Male` / `Female`
* `number_of_images`: 1-4

### Optional fields

* `background`: 背景提示词，长度上限 1500
* `detail`: 细节提示词，长度上限 1500
* `talking_pose`: 讲话姿势提示词，长度上限 1500
* `industry`: 行业提示词
* `origin`: 人种提示词，如 `Chinese`
* `aspect_ratio`: `0=9:16`，`1=16:9`
* `ref_img_url`: 参考图链接
* `ref_content`: `style` / `appearance`

### Notes

* 这个接口不接受本地文件上传，只接受远端 `ref_img_url`
* RPM 10/min，任务并发 1

## Get Photo Task

接口：

```http
GET /open/v1/aigc/photo/task?unique_id=<task_id>
```

重点返回字段：

* `unique_id`
* `type`: `1=photo`
* `progress_desc`: `Ready / Generating / Queued / Error / Success / Fail`
* `err_msg`
* `aspect_ratio`
* `output_url`: 文生图结果数组
* `waiting_num`

### Poll termination rules

* `Ready` / `Generating` / `Queued`: 继续轮询
* `Success`: 成功，取 `output_url`
* `Error` / `Fail`: 失败，停止并报错

## List Tasks

接口：

```http
GET /open/v1/aigc/photo/task/page?page=1&page_size=10
```

虽然接口名称是“文生图任务列表”，但返回里 `type=2` 也可表示 motion 任务，因此本 skill 用 `list_tasks.py` 统一展示。

重点字段：

* `unique_id`
* `type`: `1=photo`，`2=motion`
* `progress_desc`
* `output_url`
* `waiting_num`

## Create Motion Task

接口：

```http
POST /open/v1/aigc/motion
```

这是异步任务接口，响应 `data` 即图生视频任务 `unique_id`。

### Required fields

* `photo_unique_id`: 来源文生图任务 ID
* `photo_path`: 图片地址

### Optional fields

* `emotion`: 情感提示词，长度上限 800
* `gesture`: 是否启用动作

### Notes

* `photo_path` 需要是可访问的图片 URL，通常来自 `poll_photo_task.py`
* RPM 10/min，任务并发 1

## Get Motion Task

接口：

```http
GET /open/v1/aigc/motion/task?unique_id=<task_id>
```

重点返回字段：

* `unique_id`
* `type`: `2=motion`
* `progress_desc`: `Ready / Generating / Queued / Error / Success / Fail`
* `err_msg`
* `output_url`: 视频结果数组

### Poll termination rules

* `Ready` / `Generating` / `Queued`: 继续轮询
* `Success`: 成功，取 `output_url[0]`
* `Error` / `Fail`: 失败，停止并报错

## Create LoRA Task

接口：

```http
POST /open/v1/aigc/lora/task/create
```

### Required fields

* `name`: LoRA 名称
* `photos`: 训练照片 URL 数组，至少 5 张，最多 50 张

### Optional fields

* `lora_id`: 重试失败任务时传入已有任务 ID

### Notes

* 当前开放接口默认返回 1 张 LoRA 图
* 这个接口也不接受本地上传，只接受远端图片 URL

## Get LoRA Task

接口：

```http
GET /open/v1/aigc/lora/task?lora_id=<lora_id>
```

重点返回字段：

* `lora_id`
* `photo_task_ids`: 关联生成的照片任务 ID 数组
* `status`: `Queued / Published / Generating / Success / Fail`
* `err_msg`

### Poll termination rules

* `Queued` / `Published` / `Generating`: 继续轮询
* `Success`: 成功，转入 `photo_task_ids`
* `Fail`: 失败，停止并报错

## Status Codes

这些接口文档里常见状态码一致：

* `0`: 成功
* `400`: 参数格式错误
* `10400`: AccessToken 验证失败
* `40000`: 参数错误
* `40001`: 超出 RPM 限制
* `50000`: 系统内部错误

## Script Mapping

| 脚本 | 对应接口 |
|------|----------|
| `create_photo_task.py` | `POST /open/v1/aigc/photo` |
| `get_photo_task.py` | `GET /open/v1/aigc/photo/task` |
| `list_tasks.py` | `GET /open/v1/aigc/photo/task/page` |
| `poll_photo_task.py` | `GET /open/v1/aigc/photo/task` |
| `create_motion_task.py` | `POST /open/v1/aigc/motion` |
| `get_motion_task.py` | `GET /open/v1/aigc/motion/task` |
| `poll_motion_task.py` | `GET /open/v1/aigc/motion/task` |
| `create_lora_task.py` | `POST /open/v1/aigc/lora/task/create` |
| `get_lora_task.py` | `GET /open/v1/aigc/lora/task` |
| `poll_lora_task.py` | `GET /open/v1/aigc/lora/task` |
| `download_result.py` | 下载 `output_url` 到本地 |
