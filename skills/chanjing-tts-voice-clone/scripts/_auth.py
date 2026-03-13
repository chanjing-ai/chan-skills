# 鉴权：与 chanjing-credentials-guard 使用同一配置文件（CONFIG_DIR/credentials.json）
# 无 AK/SK 时执行 open_login_page 脚本打开注册/登录页
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

CONFIG_DIR = Path(os.environ.get("CHANJING_CONFIG_DIR", Path.home() / ".chanjing"))
CONFIG_FILE = CONFIG_DIR / "credentials.json"
API_BASE = os.environ.get("CHANJING_API_BASE", "https://open-api.chanjing.cc")
BUFFER_SECONDS = 300
LOGIN_URL = "https://www.chanjing.cc/openapi/login"

NO_CREDENTIALS_MSG = """已在浏览器打开蝉镜登录/注册页。
获取秘钥后请执行：
  python skills/chanjing-credentials-guard/scripts/chanjing-config --ak <你的app_id> --sk <你的secret_key>
设置完毕后请重新执行您之前的操作。"""


def _run_open_login_page():
    """执行 credentials-guard 的 open_login_page 脚本，在默认浏览器打开注册/登录页。"""
    try:
        skills_dir = Path(__file__).resolve().parent.parent.parent
        script = skills_dir / "chanjing-credentials-guard" / "scripts" / "open_login_page"
        if script.exists():
            subprocess.run([sys.executable, str(script)], check=False, timeout=5)
        else:
            import webbrowser
            webbrowser.open(LOGIN_URL)
    except Exception:
        try:
            import webbrowser
            webbrowser.open(LOGIN_URL)
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


def get_token():
    """返回 (token, None) 或 (None, error_msg)。"""
    data = read_config()
    app_id = (data.get("app_id") or "").strip()
    secret_key = (data.get("secret_key") or "").strip()
    if not app_id or not secret_key:
        _run_open_login_page()
        return None, NO_CREDENTIALS_MSG

    now = int(time.time())
    token = data.get("access_token")
    expire_in = data.get("expire_in")
    try:
        expire_in = int(expire_in) if expire_in is not None else 0
    except (ValueError, TypeError):
        expire_in = 0

    if token and expire_in > now + BUFFER_SECONDS:
        return token, None

    url = API_BASE + "/open/v1/access_token"
    req = urllib.request.Request(
        url,
        data=json.dumps({"app_id": app_id, "secret_key": secret_key}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return None, str(e)

    if body.get("code") != 0:
        return None, body.get("msg", "获取 Token 失败")

    d = body.get("data", {})
    new_token = d.get("access_token")
    if not new_token:
        return None, "API 返回无 access_token"

    data["access_token"] = new_token
    data["expire_in"] = d.get("expire_in")
    write_config(data)
    return new_token, None
