---
name: chanjing-tts
description: 使用蝉镜的TTS API将文本转为语音
---

# 蝉镜的TTS将文本转为语音

## 何时使用该技能

当用户需要从文本生成音频时调用该技能。

### 说明

Cicada-TTS提供异步语音合成API，适用于长文本的音频合成任务，单次请求长度限制小于4千字。
1. 支持多种系统音色
2. 支持语速和音调的调整
3. 支持音频时长的返回
4. 支持时间戳(字幕)返回，精确到句
5. 支持中英双语

注意: 异步语音合成，RPM 200, 具体进度通过查询接口查看

### 使用流程

需要调用多个接口，所有接口的域名都是"https://open-api.chanjing.cc"。
所有的POST请求都接受json格式的body。

1. 获取一个access\_token，后续的请求需要使用
2. 选择需要使用的音色ID
3. 调用创建语音生成任务API，记录`task_id`
4. 调用查询语音生成任务状态API，直到结果为success
5. 当任务状态完成时，使用相应中的url下载音频


#### 获取AccessToken

地址

```http
POST /open/v1/access_token
```

Header

```http
Content-Type: application/json; charset=utf-8
```

参数Body

```json
{
    "app_id": "84042cb5",
    "secret_key": "10cd5091fe6042dfb91ba01816a991e0"
}
```

响应示例

```json
{
    "trace_id": "8ff3fcd57b33566048ef28568c6cee96",
    "code": 0,
    "msg": "success",
    "data": {
        "access_token": "1208CuZcV1Vlzj8MxqbO0kd1Wcl4yxwoHl6pYIzvAGoP3DpwmCCa73zmgR5NCrNu",
        "expire_in": 1721289220
    }
}
```

响应字段说明

| 一级字段 | 二级字段 | 说明 |
| --- | --- | --- |
| code |  | 响应状态码 |
| msg |  | 响应消息 |
| data |  | 响应数据 |
|  | access\_token | 默认有效期为一天，重新获取后旧 token 即失效 |
|  | expire\_in | token过期时间 |

响应状态码说明

| code | 说明 |
| --- | --- |
| 0 | 响应成功 |
| 400 | 传入参数格式错误 |
| 40000 | 参数错误 |
| 50000 | 系统内部错误 |

#### 选择需要使用的音色ID

通过API获取当前可用的音色ID，然后从中选择适合手头任务的ID。

请求地址

```http
GET  /open/v1/list_common_audio
```

Header

```http
access_token: {{access_token}}
```

请求参数

| Key | Value |  |
| --- | --- | --- |
| page | 1 | 当前页 |
| size | 10 | 每页数量 |

响应示例

```json
{
    "trace_id": "25eb6794ffdaaf3672c25ed9efbe49c6",
    "code": 0,
    "msg": "success",
    "data": {
        "list": [
            {
                "id": "f9248f3b1b42447fb9282829321cfcf2",
                "grade": 0,
                "name": "带货小芸",
                "gender": "female",
                "lang": "multilingual",
                "desc": "",
                "speed": 1,
                "pitch": 1,
                "audition": "https://res.chanjing.cc/chanjing/res/upload/ms/2025-06-05/7945e0474b8cb526e884ee7e28e4af8d.wav"
            },
            {
                "id": "f5e69c1bbe414bec860da3294e177625",
                "grade": 0,
                "name": "方言口音老奶奶",
                "gender": "female",
                "lang": "multilingual",
                "desc": "",
                "speed": 1,
                "pitch": 1,
                "audition": "https://res.chanjing.cc/chanjing/res/upload/ms/2025-04-30/1b248ad05953028db5a6bcba9a951164.wav"
            },
            ...
        ],
        "page_info": {
            "page": 1,
            "size": 10,
            "total_count": 98,
            "total_page": 10
        }
    }
}
```

响应字段说明

| 一级字段 | 二级字段 | 三级字段 | 说明 |
| --- | --- | --- | --- |
| code |  |  | 响应状态码 |
| message |  |  | 响应消息 |
| data |  |  | 响应数据 |
|  | list | 列表数据 | 公共声音-列表数据 |
|  |  | id | 声音id |
|  |  | name | 声音人名称，其中如果包括地名，则生成的语音为方言 |
|  |  | gender | 性别 |
|  |  | lang | 语种 |
|  |  | desc | 描述 |
|  |  | speed | 音速 |
|  |  | pitch | 音调 |
|  |  | audition | 试听链接 |
|  |  | grade | 等级 |

响应状态码说明

| code | 说明 |
| --- | --- |
| 0 | 响应成功 |
| 10400 | AccessToken验证失败 |
| 40000 | 参数错误 |
| 50000 | 系统内部错误 |
| 51000 | 系统内部错误 |

#### 调用创建语音生成任务API

请求路径

```http
POST /open/v1/create_audio_task
```

Header

```http
access_token: {{access_token}}
Content-Type: application/json
```

请求参数json字段

| **参数名称** | **类型** | **Nested Key** | **是否必传** | **示例** | **说明** |
| --- | --- | --- | --- | --- | --- |
| audio\_man | string |  | 是 | 89843d52ccd04e2d854decd28d6143ce  | 声音ID |
| speed | number |  | 是 | 1 | 语速（范围:0.5x～2x） |
| pitch | number |  | 是 | 1 | 语调（固定为1） |
| text | object | text | 是 | 你好，我是你的蝉镜数字人 | 富文本，文本长度限制为4000字以下 |
| aigc\_watermark | bool |  | 否 | false | 音频是否加明水印，默认是false |

请求示例

```json
{
    "audio_man": "89843d52ccd04e2d854decd28d6143ce ",
    "speed": 1,
    "pitch": 1,
    "text": {
        "text": "你好，我是你的蝉镜数字人",
    },
}
```

响应参数json字段

| **字段** | **说明** |
| --- | --- |
| code | 响应状态码 |
| msg | 响应消息 |
| task\_id | 语音合成任务ID |


示例响应

```json
{
    "trace_id": "dd09f123a25b43cf2119a2449daea6de",
    "code": 0,
    "msg": "success",
    "data": {
        "task_id": "88f635dd9b8e4a898abb9d4679e0edc8"
    }
}
```

响应状态码说明

| code | 说明 |
| --- | --- |
| 0 | 响应成功 |
| 400 | 传入参数格式错误 |
| 10400 | AccessToken验证失败 |
|  | APP状态错误 |
|  | 缺少 tts 文本 |
|  | 缺少音频文件 |
|  | 输入文本不可以包含 emoji |
| 40000 | 参数错误 |
| 40001 | 超出QPS限制 |
| 40002 | 制作时长到达上限 |
| 50000 | 系统内部错误 |
|  | 没有找到对应的声音ID |
|  | 声音ID对应的audio\_man不存在或被禁用 |

#### 调用查询语音生成任务状态API

请求地址

```http
POST /open/v1/audio_task_state
```

Header

```http
access_token: {{access_token}}
Content-Type: application/json
```

请求参数Body

| **参数名称** | **类型** | **是否必传** | **示例** | **说明** |
| --- | --- | --- | --- | --- |
| task\_id | string | 是 | 88f789dd9b8e4a121abb9d4679e0edc8 | 语音合成任务ID |

响应JSON

```json
{
    "trace_id": "ab18b14574bbcc31df864099d474080e",
    "code": 0,
    "msg": "success",
    "data": {
        "id": "9546a0fb1f0a4ae3b5c7489b77e4a94d",
        "type": "tts",
        "status": 9,
        "text": [
            "猫在跌落时能够在空中调整身体，通常能够四脚着地，这种”猫右自己“反射显示了它们惊人的身体协调能力和灵活性。核磁共振成像技术通过利用人体细胞中氢原子的磁性来生成详细的内部图像，为医学诊断提供了重要工具。"
        ],
        "full": {
            "url": "https://cy-cds-test-innovation.cds8.cn/chanjing/res/upload/tts/2025-04-08/093a59021d85a72d28a491f21820ece4.wav",
            "path": "093a59013d85a72d28a491f21820ece4.wav",
            "duration": 18.81
        },
        "slice": null,
        "errMsg": "",
        "errReason": "",
        "subtitles": [
            {
                "key": "20c53ff8cce9831a8d9c347263a400a54d72be15",
                "start_time": 0,
                "end_time": 2.77,
                "subtitle": "猫在跌落时能够在空中调整身体"
            },
            {
                "key": "e19f481b6cd2219225fa4ff67836448e054b2271",
                "start_time": 2.77,
                "end_time": 4.49,
                "subtitle": "通常能够四脚着地"
            },
            {
                "key": "140beae4046bd7a99fbe4706295c19aedfeeb843",
                "start_time": 4.49,
                "end_time": 5.73,
                "subtitle": "这种，猫右自己"
            },
            {
                "key": "e851881271876ab5a90f4be754fde2dc6b5498fd",
                "start_time": 5.73,
                "end_time": 7.97,
                "subtitle": "反射显示了它们惊人的身体"
            },
            {
                "key": "fbb0b4138bad189b9fc02669fe1f95116e9991b4",
                "start_time": 7.97,
                "end_time": 9.45,
                "subtitle": "协调能力和灵活性"
            },
            {
                "key": "f73404d135feaf84dd8fbea13af32eac847ac26d",
                "start_time": 9.45,
                "end_time": 12.49,
                "subtitle": "核磁共振成像技术通过利用人体"
            },
            {
                "key": "e18827931223962e477b14b2b8046947039ac222",
                "start_time": 12.49,
                "end_time": 14.77,
                "subtitle": "细胞中氢原子的磁性来生成"
            },
            {
                "key": "d137bf2b0c8b7a39e3f6753b7cf5d92bd877d2d9",
                "start_time": 14.77,
                "end_time": 15.97,
                "subtitle": "详细的内部图像"
            },
            {
                "key": "0773911ae0dbaa763a64352abdb6bdac3ff8f149",
                "start_time": 15.97,
                "end_time": 18.41,
                "subtitle": "为医学诊断提供了重要工具"
            }
        ]
    }
}
```

响应字段说明

| 一级字段 | 二级字段 | 三级字段 | 说明 |
| --- | --- | --- | --- |
| code |  |  | 响应状态码 |
| msg |  |  | 响应消息 |
| data | id |  | 视频id |
|  | type |  | 语音类型 |
|  | status |  | 状态:1 生成中、9 生成完毕(包含成功与失败) |
|  | text |  | 语音文本 |
|  | full | url | 音频链接 |
|  |  | path | 音频地址 |
|  |  | duration | 音频时长 |
|  | slice |  | 切片 |
|  | errMsg |  | 错误信息 |
|  | errReason |  | 错误理由 |
|  | subtitles(数组类型) | key | 字幕key值 |
|  |  | start\_time | 字幕开始时间点 |
|  |  | end\_time | 字幕结束时间点 |
|  |  | subtitle | 字幕文本 |

响应状态码说明

| code | 说明 |
| --- | --- |
| 0 | 响应成功 |
| 10400 | AccessToken验证失败 |
|  | APP状态错误 |
| 40000 | 参数错误 |
| 50000 | 系统内部错误 |
