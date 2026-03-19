---
name: chanjing-credentials-guard
description: Run this skill before any chanjing-related action. When the user asks to generate or configure chanjing credentials/keys (AK/SK), run this skill to guide them—check if already configured; if yes, ask whether to re-apply; then open login page and let the user either run the config command or paste AK/SK for the agent to apply. ALWAYS run when user asks for chanjing credentials/keys or before any chanjing API (voice list, TTS, avatar, voice-clone).
---

# Chanjing Credentials Guard

## When to Run

1. **Before any other Chanjing skill**: Run this skill first to validate credentials; if missing, guide the user.
2. **When the user asks to generate chanjing keys, get keys, or configure AK/SK**: Run this skill and follow the “Guide to generate keys” flow below.

Before calling any Chanjing API (list voices, TTS, avatar, voice clone, etc.), credentials must be validated.

## Execution Flow

```
1. Check if local AK/SK exists
   └─ No  → Run open_login_page (open login in browser) → Offer two setup options (user runs command, or pastes AK/SK for the agent to apply) → After config, continue the original action without asking the user to re-run it
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
2. **Offer two setup options** after the user obtains keys:
   - Option A: show the command for the user to run locally.
   - Option B: let the user paste `AK=... SK=...` in chat and apply it for them by running `python skills/chanjing-credentials-guard/scripts/chanjing-config --ak ... --sk ...`.
3. **Continue automatically after setting**: Once AK/SK is saved successfully, continue the original skill flow in the same conversation. Do not ask the user to re-run their previous action.
4. **Handle secrets carefully**:
   - Tell the user AK/SK is sensitive and chat history may retain it.
   - If the user chooses chat-based setup, do not echo the full values back.
   - Only confirm with masked output such as `AK=abcd****`, `SK=wxyz****`.
   - Do not print the full secret in summaries or follow-up messages.

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
3. **Offer two ways to configure AK/SK** after the user obtains `app_id` and `secret_key`:
   ```bash
   python skills/chanjing-credentials-guard/scripts/chanjing-config --ak <your_app_id> --sk <your_secret_key>
   ```
   The user may either:
   - run the command themselves, or
   - paste `AK=<your_app_id> SK=<your_secret_key>` in chat so the agent can run the command for them.
4. **When the user pastes AK/SK in chat**:
   - treat the values as sensitive,
   - run the config command on the user's machine,
   - avoid echoing full secrets back,
   - continue the original task after successful config instead of stopping.
5. **After setting**: Config is saved and Chanjing skills can be used immediately. If this flow was triggered by another action, continue that action automatically. For re-apply, the command above overwrites the existing config.

You can run `python skills/chanjing-credentials-guard/scripts/open_login_page` first to open the login page, then either run the config command yourself or paste `AK=... SK=...` in the conversation for the agent to apply.

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

# Set AK/SK manually
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
