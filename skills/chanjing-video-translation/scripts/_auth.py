#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path


def _config_dir():
    raw = os.environ.get("CHANJING_OPENAPI_CREDENTIALS_DIR") or os.environ.get("CHANJING_CONFIG_DIR")
    return Path(raw).expanduser() if raw else Path.home() / ".chanjing"


def _api_base():
    return (os.environ.get("CHANJING_OPENAPI_BASE_URL") or os.environ.get("CHANJING_API_BASE") or "https://open-api.chanjing.cc").rstrip("/")


CONFIG_DIR = _config_dir()
CONFIG_FILE = CONFIG_DIR / "credentials.json"
API_BASE = _api_base()


def _open_login_page():
    script = Path(__file__).resolve().parents[2] / "chanjing-credentials-guard" / "scripts" / "open_login_page.py"
    if script.exists():
        subprocess.run([sys.executable, str(script)], check=False, timeout=5)


def get_token():
    try:
        config = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except FileNotFoundError:
        config = {}
    except json.JSONDecodeError as exc:
        return None, f"credentials.json 格式错误: {exc}"

    app_id = (config.get("app_id") or "").strip()
    secret_key = (config.get("secret_key") or "").strip()
    if not app_id or not secret_key:
        _open_login_page()
        return None, "缺少 app_id 或 secret_key，请先配置 chanjing-credentials-guard"

    try:
        valid_until = int(config.get("expire_in") or 0)
    except (TypeError, ValueError):
        valid_until = 0
    token = config.get("access_token")
    if token and valid_until > int(time.time()) + 300:
        return token, None

    request = urllib.request.Request(
        API_BASE + "/open/v1/access_token",
        data=json.dumps({"app_id": app_id, "secret_key": secret_key}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        return None, str(exc)
    if body.get("code") != 0 or not body.get("data", {}).get("access_token"):
        return None, body.get("msg", "获取 Token 失败")

    config.update(body["data"])
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    return config["access_token"], None
