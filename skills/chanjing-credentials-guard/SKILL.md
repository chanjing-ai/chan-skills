---
name: chanjing-credentials-guard
description: Run this skill before any chanjing-related action. When the user asks to generate or configure chanjing credentials/keys (AK/SK), run this skill to guide them—check if already configured; if yes, ask whether to re-apply; then open login page and show config commands. ALWAYS run when user asks for chanjing credentials/keys or before any chanjing API (voice list, TTS, avatar, voice-clone).
---

# Chanjing Credentials Guard

## When to Run

1. **Before any other Chanjing skill**: Run this skill first to validate credentials; if missing, guide the user.
2. **When the user asks to generate chanjing keys, get keys, or configure AK/SK**: Run this skill and follow the “Guide to generate keys” flow below.

Before calling any Chanjing API (list voices, TTS, avatar, voice clone, etc.), credentials must be validated.

## Execution Flow

```
1. Check if local AK/SK exists
   └─ No  → Run open_login_page (open login in browser) → Show user the command to set AK/SK → Stop (user must re-run their original action after setting)
   └─ Yes → Continue

2. Check if local Token exists and is not expired
   └─ No  → Call API to request/refresh Token → Save
   └─ Yes → Continue

3. Continue with the target Skill
```

## Credential Storage (AK/SK read from config file)

AK/SK and Token are read from the **same config file**. Path and format follow the script **`scripts/chanjing-config`** in this skill.

- **Path**: `~/.chanjing/credentials.json` (overridable by env `CHANJING_CONFIG_DIR`)
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

1. **Open login page**: Run the `open_login_page` script to open the Chanjing sign-in page in the default browser (`https://www.chanjing.cc/openapi/login`).
2. **Show set AK/SK command**: Output the command for the user to run after obtaining keys.
3. **After setting**: Tell the user to **re-run their previous action** (or the current command) so credentials are validated again.

Commands to set AK/SK (use either):

```bash
python scripts/chanjing-config --ak <your_app_id> --sk <your_secret_key>
python skills/chanjing-credentials-guard/scripts/chanjing-config --ak <your_app_id> --sk <your_secret_key>
```

To open the login page manually: `python skills/chanjing-credentials-guard/scripts/open_login_page`

## Guide When User Wants to Generate Keys

When the user clearly wants to **generate chanjing keys**, **get keys**, or **configure AK/SK**, follow this flow:

### Step 1: Check if already configured

Check if local AK/SK already exists (read `~/.chanjing/credentials.json` for non-empty `app_id` and `secret_key`, or run `python skills/chanjing-credentials-guard/scripts/chanjing-config --status`).

### Step 2: Branch on result

- **If already configured**: Ask the user—**“You already have Chanjing AK/SK configured. Do you want to re-apply and overwrite the current config?”**
  - If the user confirms re-apply, run the “Guide steps” below.
  - If the user says no, stop; do not open the login page or show config commands.

- **If not configured**: Run the “Guide steps” below directly.

### Guide steps (when not configured or user confirmed re-apply)

1. **Run `open_login_page`** to open the Chanjing login page in the default browser.
2. **Explain the page flow clearly**:
   - New users are registered automatically and the current page will display `App ID` and `Secret Key` with copy buttons.
   - Existing users may be redirected to the console; tell them to open the left-side **API 密钥** page to view or reset keys.
3. **Output the set AK/SK command** and tell the user to run it in the terminal after obtaining `app_id` and `secret_key`:
   ```bash
   python skills/chanjing-credentials-guard/scripts/chanjing-config --ak <your_app_id> --sk <your_secret_key>
   ```
4. **After setting**: Config is saved and Chanjing skills can be used; if this was triggered by another action, the user can re-run that action. For re-apply, the command above overwrites the existing config.

You can run `python skills/chanjing-credentials-guard/scripts/open_login_page` first to open the login page, then paste the config command in the conversation.

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

1. **AK/SK**: Read from config (path/format above, per `chanjing-config`); ensure `app_id` and `secret_key` are non-empty.
2. **Token**: Ensure `access_token` exists and `expire_in > current_time + 300` (refresh 5 minutes early).
3. **Token refresh**: Call the API above and write returned `access_token` and `expire_in` back to the file.

**Shortcut**: Run `python skills/chanjing-credentials-guard/scripts/chanjing-get-token`; on success it prints access_token, on failure it prints guidance.

## Shell Config

| Script | Description |
|--------|-------------|
| `open_login_page` | Opens the Chanjing login page and explains how new/existing users obtain AK/SK |
| `chanjing-config` | Set or view AK/SK and Token status |

```bash
# Open login page (also runs automatically when AK/SK is missing)
python skills/chanjing-credentials-guard/scripts/open_login_page

# Set AK/SK (after setting, user should re-run their previous action)
python skills/chanjing-credentials-guard/scripts/chanjing-config --ak <app_id> --sk <secret_key>

# View status
python skills/chanjing-credentials-guard/scripts/chanjing-config --status
```

## With Other Skills

- **chanjing-tts**, **chanjing-avatar**, **chanjing-tts-voice-clone**, etc. must pass this credentials guard before running.
- If the agent already has a token from MCP `user-chanjing` `get_access_token`, it may use that; otherwise complete local validation and token preparation first.

## Reference

- [reference.md](reference.md): API and storage format details
- chanjing-openapi.yaml: `/access_token`, `dto.OpenAccessTokenReq`, `dto.OpenAccessTokenResp`
