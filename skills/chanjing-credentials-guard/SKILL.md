---
name: chanjing-credentials-guard
description: >-
  Guide users to configure local Chanjing credentials safely via local
  commands only, and validate local token status when needed.
credential: credentials.json (app_id/secret_key; access_token persisted on disk)
openclaw_primary_env: false
environment: CHANJING_OPENAPI_CREDENTIALS_DIR, CHANJING_OPENAPI_BASE_URL
legacy_environment: CHANJING_CONFIG_DIR, CHANJING_API_BASE
machine_readable: manifest.yaml
requires_ffmpeg: false
requires_ffprobe: false
notes: Do not request secrets in chat; use local scripts only.
---

# Chanjing Credentials Guard

## 功能说明

仅通过**本地命令**引导用户配置/校验蝉镜 **AK/SK** 与 **Token**，打开登录页；**不在对话中索取密钥**。可配合其它 Chanjing 技能使用。

## 运行依赖

- **python3** 与 `scripts/chanjing_config.py`、`scripts/open_login_page.py`、`scripts/chanjing_get_token.py` 等

## 环境变量与机器可读声明

- 环境变量键名与说明：**`manifest.yaml`**（`environment` 段）及本文
- 变量、写盘路径与权限：**`manifest.yaml`**

## 使用命令

- **ClawHub**（slug 以注册表为准）：`clawhub run chanjing-credentials-guard`
- **本仓库**：`python skills/chanjing-credentials-guard/scripts/chanjing_config.py --status`

---

## When to Run

1. **When user asks to configure/get Chanjing keys (AK/SK)**: use this skill to guide local setup.
2. **When credentials are missing/invalid before a Chanjing API call**: use this skill to recover local config.

This skill is a **local credential guide**, not a cross-skill runtime dependency.

## Execution Flow

```
1. Check if local AK/SK exists
   └─ No  → Run open_login_page.py (open login in browser) → Ask user to run local config command
   └─ Yes → Continue

2. Check if local Token exists and is not expired
   └─ No  → Call API to request/refresh Token → Save
   └─ Yes → Continue

3. Prompt user to continue target action
```

## Credential Storage (AK/SK read from config file)

AK/SK and Token are read from the **same config file**. Path and format follow the script **`scripts/chanjing_config.py`** in this skill.

- **Path**: `~/.chanjing/credentials.json`（目录由 **`CHANJING_OPENAPI_CREDENTIALS_DIR`** 覆盖，兼容 **`CHANJING_CONFIG_DIR`**）
- **Format**:
```json
{
  "app_id": "Your Access Key",
  "secret_key": "Your Secret Key",
  "access_token": "Optional, auto-generated",
  "expire_in": 1721289220
}
```

`expire_in` is a Unix timestamp. Token is valid for about 24 hours; refresh 5 minutes before expiry.

## When AK/SK Is Missing

When local `app_id` or `secret_key` is missing:

1. **Open login page**: Run the `open_login_page.py` script to open the Chanjing sign-in page in the default browser (`https://www.chanjing.cc/openapi/login`).
2. **Require local setup command** after the user obtains keys:
   - Show command only; user runs it locally in terminal.
3. **Do not request secrets in chat**:
   - Never ask user to paste AK/SK in conversation.
   - Never echo or store AK/SK in chat summaries.
4. **After setting**:
   - Ask user to run status check and then proceed to target action.

Commands to set AK/SK (use either):

```bash
python scripts/chanjing_config.py --ak <your_app_id> --sk <your_secret_key>
python skills/chanjing-credentials-guard/scripts/chanjing_config.py --ak <your_app_id> --sk <your_secret_key>
```

To open the login page manually: `python skills/chanjing-credentials-guard/scripts/open_login_page.py`

## Guide When User Wants to Generate Keys

When the user clearly wants to **generate chanjing keys**, **get keys**, or **configure AK/SK**, follow this flow:

### Step 1: Check if already configured

Check if local AK/SK already exists (read `~/.chanjing/credentials.json` for non-empty `app_id` and `secret_key`, or run `python skills/chanjing-credentials-guard/scripts/chanjing_config.py --status`).

### Step 2: Branch on result

- **If already configured**: ask whether user wants to overwrite local config.
  - If yes, run guide steps.
  - If no, stop.

- **If not configured**: Run the “Guide steps” below directly.

### Guide steps (when not configured or user confirmed re-apply)

1. **Run `open_login_page.py`** to open the Chanjing login page in the default browser.
2. **Explain the page flow clearly**:
   - New users are registered automatically and the current page will display `App ID` and `Secret Key` with copy buttons.
   - Existing users may be redirected to the console; tell them to open the left-side **API 密钥** page to view or reset keys.
3. **Ask user to run local command to configure AK/SK**:
   ```bash
   python skills/chanjing-credentials-guard/scripts/chanjing_config.py --ak <your_app_id> --sk <your_secret_key>
   ```
4. **Secret handling rule**:
   - Do not ask user to paste AK/SK in chat.
   - If user shares secret in chat anyway, remind them to rotate keys and continue with local-command-only flow.
5. **After setting**:
   - Run status check:
     `python skills/chanjing-credentials-guard/scripts/chanjing_config.py --status`
   - Then proceed to target Chanjing action.

## Token API (see chanjing-openapi.yaml)

```http
POST https://open-api.chanjing.cc/open/v1/access_token
Content-Type: application/json
```

Request body:
```json
{
  "app_id": "{{app_id}}",
  "secret_key": "{{secret_key}}"
}
```

Response (success `code: 0`):
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "access_token": "xxx",
    "expire_in": 1721289220
  }
}
```

- `expire_in`: Unix timestamp for token expiry
- If `code !== 0`, AK/SK is invalid or the request failed

## Validation Logic

1. **AK/SK**: Read from config (path/format above, per `chanjing_config.py`); ensure `app_id` and `secret_key` are non-empty.
2. **Token**: Ensure `access_token` exists and `expire_in > current_time + 300` (refresh 5 minutes early).
3. **Token refresh**: Call the API above and write returned `access_token` and `expire_in` back to the file.

**Shortcut**: Run `python skills/chanjing-credentials-guard/scripts/chanjing_get_token.py`; on success it prints access_token, on failure it prints guidance.

## Security Boundary

- This skill only handles **local credential guidance**.
- It does not require install hooks or elevated/system-wide privileges.
- It should not automatically execute unrelated skills.
- It should not accept AK/SK via chat content.

## Shell Config

| Script | Description |
|--------|-------------|
| `open_login_page.py` | Opens the Chanjing login page and explains how new/existing users obtain AK/SK |
| `chanjing_config.py` | Set or view AK/SK and Token status |
| `chanjing_get_token.py` | Print a valid `access_token` to stdout (or guidance on failure) |

```bash
# Open login page (also runs automatically when AK/SK is missing)
python skills/chanjing-credentials-guard/scripts/open_login_page.py

# Set AK/SK manually
python skills/chanjing-credentials-guard/scripts/chanjing_config.py --ak <app_id> --sk <secret_key>

# View status
python skills/chanjing-credentials-guard/scripts/chanjing_config.py --status
```

## With Other Skills

- Other Chanjing skills may use the same local config path/format, but should keep their own runtime auth logic.
- Guard can be used as an optional setup helper when users explicitly ask for credential guidance.

## Reference

- [reference.md](reference.md): API and storage format details
- chanjing-openapi.yaml: `/access_token`, `dto.OpenAccessTokenReq`, `dto.OpenAccessTokenResp`
