#!/usr/bin/env python3
"""
获取有效的 access_token。
AK/SK 从与 chanjing_config.py 相同的配置文件中读取（CONFIG_DIR/credentials.json，见 chanjing_config.py）。
若无 AK/SK 则输出引导信息并退出；若 Token 过期则自动申请并保存。
用法: python chanjing_get_token.py
输出: 成功时打印 access_token 到 stdout；失败时打印错误到 stderr 并 exit 1
"""
import json
import os
import sys
import urllib.request
from pathlib import Path

_DEFAULT_OPENAPI_BASE = "https://open-api.chanjing.cc"


def credentials_config_dir() -> Path:
    raw = os.environ.get("CHANJING_OPENAPI_CREDENTIALS_DIR") or os.environ.get("CHANJING_CONFIG_DIR")
    return Path(raw).expanduser() if raw else Path.home() / ".chanjing"


def openapi_base_url() -> str:
    return (
        os.environ.get("CHANJING_OPENAPI_BASE_URL")
        or os.environ.get("CHANJING_API_BASE")
        or _DEFAULT_OPENAPI_BASE
    ).rstrip("/")


CONFIG_DIR = credentials_config_dir()
CONFIG_FILE = CONFIG_DIR / "credentials.json"
API_URL = openapi_base_url() + "/open/v1/access_token"
BUFFER_SECONDS = 300  # 提前 5 分钟刷新


def _run_open_login_page():
    """在默认浏览器打开蝉镜登录页。"""
    try:
        import webbrowser
        webbrowser.open("https://www.chanjing.cc/openapi/login")
    except Exception:
        try:
            import webbrowser
            webbrowser.open("https://www.chanjing.cc/openapi/login")
        except Exception:
            pass


def read_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def write_config(data):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    try:
        os.chmod(CONFIG_FILE, 0o600)
    except OSError:
        pass


def fetch_token(app_id, secret_key):
    req = urllib.request.Request(
        API_URL,
        data=json.dumps({"app_id": app_id, "secret_key": secret_key}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    return body


def main():
    data = read_config()
    app_id = data.get("app_id", "").strip()
    secret_key = data.get("secret_key", "").strip()

    if not app_id or not secret_key:
        _run_open_login_page()
        print(
            "已在浏览器打开蝉镜登录/注册页。",
            "获取秘钥后请执行：",
            "  python skills/chanjing-credentials-guard/scripts/chanjing_config.py --ak <你的app_id> --sk <你的secret_key>",
            "设置完毕后请重新执行您之前的操作或当前命令。",
            sep="\n",
            file=sys.stderr,
        )
        sys.exit(1)

    import time
    now = int(time.time())
    token = data.get("access_token")
    expire_in = data.get("expire_in")
    try:
        expire_in = int(expire_in) if expire_in is not None else 0
    except (ValueError, TypeError):
        expire_in = 0

    if token and expire_in > now + BUFFER_SECONDS:
        print(token)
        return 0

    # 申请新 Token
    try:
        resp = fetch_token(app_id, secret_key)
    except Exception as e:
        print(f"请求 Token 失败: {e}", file=sys.stderr)
        sys.exit(1)

    if resp.get("code") != 0:
        msg = resp.get("msg", "未知错误")
        print(f"获取 Token 失败 (code={resp.get('code')}): {msg}", file=sys.stderr)
        sys.exit(1)

    d = resp.get("data", {})
    new_token = d.get("access_token")
    new_expire = d.get("expire_in")
    if not new_token:
        print("API 返回无 access_token", file=sys.stderr)
        sys.exit(1)

    data["access_token"] = new_token
    data["expire_in"] = new_expire
    write_config(data)
    print(new_token)
    return 0


if __name__ == "__main__":
    sys.exit(main())
