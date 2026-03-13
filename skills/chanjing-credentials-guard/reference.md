# Credentials Guard Reference

## API (chanjing-openapi.yaml)

### Get Access Token

| Item | Value |
|------|--------|
| Method | POST |
| URL | `https://open-api.chanjing.cc/open/v1/access_token` |
| Content-Type | application/json |

**Request body** (dto.OpenAccessTokenReq):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| app_id | string | Yes | Access Key (AK) |
| secret_key | string | Yes | Secret Key (SK) |

**Response** (success code=0):

| Field | Type | Description |
|-------|------|-------------|
| code | int | 0 = success |
| msg | string | Message |
| data.access_token | string | API credential |
| data.expire_in | int | Unix timestamp, token expiry |

**Error codes**:

| code | Description |
|------|-------------|
| 0 | Success |
| 400 | Invalid parameter format |
| 40000 | Parameter error |
| 50000 | Internal error |

## Credential storage format

AK/SK are read from a config file. Path and format follow **`scripts/chanjing-config`** (see `CONFIG_DIR`, `CONFIG_FILE`, and `read_config()` in that script).

File path: `~/.chanjing/credentials.json` (default; override with env `CHANJING_CONFIG_DIR`)

```json
{
  "app_id": "Access Key",
  "secret_key": "Secret Key",
  "access_token": "From API, optional",
  "expire_in": 1721289220
}
```

- `expire_in` is a Unix timestamp
- Token is valid for about 24 hours
- Refresh 5 minutes (300 seconds) before expiry

## Environment variables

| Variable | Description | Default |
|----------|-------------|---------|
| CHANJING_CONFIG_DIR | Credentials directory | ~/.chanjing |
| CHANJING_API_BASE | API base URL | https://open-api.chanjing.cc |

## Login and obtaining keys

- Sign up / Login: https://www.chanjing.cc/openapi/login
- Docs: https://doc.chanjing.cc
