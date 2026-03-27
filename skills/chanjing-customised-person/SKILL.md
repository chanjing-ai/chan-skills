---
name: chanjing-customised-person
description: >-
  Use Chanjing customised person APIs to create, inspect, list, poll, and
  delete custom digital humans from uploaded source videos.
credential: credentials.json (app_id/secret_key; access_token and expire_in persisted on disk; same file as chanjing-credentials-guard)
openclaw_primary_env: false
environment: CHANJING_OPENAPI_CREDENTIALS_DIR, CHANJING_OPENAPI_BASE_URL
legacy_environment: CHANJING_CONFIG_DIR, CHANJING_API_BASE
machine_readable: manifest.yaml
requires_ffmpeg: false
requires_ffprobe: false
notes: >-
  Reads ~/.chanjing/credentials.json; may open browser if AK/SK missing.
  Upload path: GET create_upload_url then HTTPS PUT to API-returned sign_url
  (host may differ from open-api). Optional --callback URL may receive sensitive
  POST payloads from Chanjing.
---

# Chanjing Customised Person

## 功能说明

从本机**上传源视频**创建蝉镜**定制数字人**，并支持列表、查询、轮询与删除；流程与 Open API 一致：**获取上传 URL**（`create_upload_url`）→ 对返回的 `sign_url` 发起 **`PUT`** 上传正文 → **创建/列出/获取/轮询/删除**。仅使用蝉镜 Open API 与接口返回的上传端点，**不**引入其它云厂商凭证。脚本**不**依赖 ffmpeg/ffprobe。环境变量**均可选**（默认 `~/.chanjing` 与官方 API 基址）。凭据、令牌持久化、网络边界见 **`manifest.yaml`**。

## 运行依赖

- **python3** 与同仓库 `scripts/*.py`；可读本地视频文件路径并上传

## 环境变量与机器可读声明

- 环境变量键名与说明：**`manifest.yaml`**（`environment` 段）及本文
- 变量键名、凭据模型、合规 **`permissions`**、**`clientPermissions`、`agentPolicy`**：**`manifest.yaml`**

## 使用命令

- **ClawHub**（slug 以注册表为准）：`clawhub run chanjing-customised-person`
- **本仓库**：`python skills/chanjing-customised-person/scripts/create_person.py …`（见 **Standard Workflow**）

---

## 登记与审稿（单一事实来源）

英文登记、主凭据、`primaryEnv` 省略、可选 env、敏感字段与出站边界：**以同目录 `manifest.yaml` 为准**（与 **`credential_hint`**、**`description` frontmatter** 一致）。本篇从 **When to Use** 起写业务能力与流程，**勿与 `manifest.yaml` 重复维护长篇对表**。

## When to Use This Skill

当用户要做这些事时使用本 Skill：

* 上传真人源视频，创建蝉镜定制数字人
* 查询定制数字人列表或单个形象详情
* 轮询定制数字人制作进度
* 删除不再需要的定制数字人

如果需求是“拿已有数字人去合成口播视频”，优先使用 `chanjing-video-compose`。  
如果需求是“上传真人视频做对口型驱动”，优先使用 `chanjing-avatar`。

## Preconditions

执行本 Skill 前，必须先通过 `chanjing-credentials-guard` 完成 AK/SK 与 Token 校验。

本 Skill 与 guard 共用：

* `~/.chanjing/credentials.json`
* `https://open-api.chanjing.cc`

无凭证时，脚本会自动打开蝉镜登录页，并提示配置命令。

### 审阅与安全（凭据与边界）

与 **Purpose / Credentials / Persistence / Network** 相关的逐项说明见 **`manifest.yaml`**（含 **`permissions.network_mode: open`** 与 **`signUrlPutNote`**）。以下仅 **SKILL 正文补充**：

- **`credentials.json`**：脚本会读取本地凭据；刷新后的 **`access_token` / `expire_in` 写回同一文件**为**预期行为**。须限制目录/文件权限（如目录 `0700`、文件 `0600`），并**确保永不提交版本库**（见 manifest **`doNotCommitToVcs`**）。
- **`sign_url` 与 PUT 主机**：`upload_file.py` / `get_upload_url.py` 先请求 `open-api.chanjing.cc` 的 `create_upload_url`，再向响应中的 **`sign_url` 发起 HTTPS PUT**；该 URL 的主机常为蝉镜侧对象存储或 CDN，**可能不在**固定主机白名单中，清单中已改为 **`network_mode: open`** 以如实声明。
- **`create_person.py --callback`**：若传入 URL，远程服务可能向该端点 **POST** 任务结果，载荷可能含状态与资源引用等**敏感信息**；须自行信任该端点并承担出站与数据暴露风险。
- **本地视频**：仅按用户给出的路径读取视频字节并上传到 API 指定端点；不扫描其它无关系统路径。

## Standard Workflow

1. 上传本地源视频，获取 `file_id`（推荐 `upload_file.py`：内部为 **`GET …/create_upload_url` → `PUT sign_url`（正文为文件）→ 轮询 `file_detail` 至就绪**；亦可分步用 `get_upload_url.py` + 自行 PUT + 轮询）
2. 调用 `create_person.py` 创建定制数字人任务，得到 `person_id`
3. 调用 `poll_person.py` 轮询直到成功，得到 `preview_url`，或用 `get_person --field audio_man_id` 拿到声音 id
4. 如需批量查看历史形象，用 `list_persons.py`
5. 如需清理资源，用 `delete_person.py`

## Covered APIs

本 Skill 当前覆盖：

* `GET /open/v1/common/create_upload_url`
* `GET /open/v1/common/file_detail`
* `POST /open/v1/create_customised_person`
* `POST /open/v1/list_customised_person`
* `GET /open/v1/customised_person`
* `POST /open/v1/delete_customised_person`

## Scripts

脚本目录：

* `skills/chanjing-customised-person/scripts/`

| 脚本 | 说明 |
|------|------|
| `_auth.py` | 读取凭证、获取或刷新 `access_token` |
| `get_upload_url.py` | 调用 `create_upload_url`，输出 `sign_url`、`mime_type`、`file_id` 等 JSON（需自行 PUT） |
| `upload_file.py` | `create_upload_url` + **HTTPS PUT `sign_url`** + 轮询 `file_detail`，输出 `file_id` |
| `create_person.py` | 创建定制数字人任务，输出 `person_id`；可选 **`--callback`**（服务端可能向该 URL **POST** 敏感任务载荷） |
| `list_persons.py` | 列出定制数字人形象 |
| `get_person.py` | 获取单个数字人详情，默认输出 JSON |
| `poll_person.py` | 轮询形象详情直到完成，默认输出 `preview_url` |
| `delete_person.py` | 删除定制数字人，输出被删除的 `person_id` |

## Usage Examples

示例 1：从本地视频创建定制数字人

```bash
FILE_ID=$(python3 skills/chanjing-customised-person/scripts/upload_file.py \
  --file ./source.mp4)

PERSON_ID=$(python3 skills/chanjing-customised-person/scripts/create_person.py \
  --name "演示数字人" \
  --file-id "$FILE_ID" \
  --train-type figure)

python3 skills/chanjing-customised-person/scripts/poll_person.py --id "$PERSON_ID"
```

示例 2：查看完整详情

```bash
python3 skills/chanjing-customised-person/scripts/get_person.py \
  --id "C-ef91f3a6db3144ffb5d6c581ff13c7ec"
```

示例 3：列出与删除

```bash
python3 skills/chanjing-customised-person/scripts/list_persons.py

python3 skills/chanjing-customised-person/scripts/delete_person.py \
  --id "C-ef91f3a6db3144ffb5d6c581ff13c7ec"
```

## Output Convention

默认不自动下载任何预览视频或封面图：

* `create_person.py` 输出 `person_id`
* `poll_person.py` 输出 `preview_url`，便于继续预览或保存
* 只有在用户明确要求时，才应把返回的资源 URL 另存到本地

如果后续需要落盘预览资源，建议使用：

* `outputs/customised-person/`

## Additional Resources

更多接口细节与触发样例见：

* `skills/chanjing-customised-person/reference.md`
* `skills/chanjing-customised-person/examples.md`
