#!/usr/bin/env python3
"""
打开蝉镜 AK/SK 注册/登录页面。无参数直接运行即可。
用法: python open_login_page.py  或  python skills/chanjing-credentials-guard/scripts/open_login_page.py
"""
import platform
import shutil
import subprocess
import webbrowser

LOGIN_URL = "https://www.chanjing.cc/openapi/login"


def _run_open_command(command, method_name):
    try:
        subprocess.run(
            command,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
        return True, method_name, None
    except subprocess.CalledProcessError as exc:
        error = (exc.stderr or "").strip() or str(exc)
        return False, method_name, error
    except OSError as exc:
        return False, method_name, str(exc)


def _command_attempts():
    system = platform.system()

    if system == "Darwin":
        return [(["open", LOGIN_URL], "macOS open")]

    if system == "Windows":
        return [(["cmd", "/c", "start", "", LOGIN_URL], "Windows start")]

    attempts = []
    if shutil.which("xdg-open"):
        attempts.append((["xdg-open", LOGIN_URL], "xdg-open"))
    if shutil.which("gio"):
        attempts.append((["gio", "open", LOGIN_URL], "gio open"))
    return attempts


def open_login_url():
    errors = []

    for command, method_name in _command_attempts():
        opened, used_method, error = _run_open_command(command, method_name)
        if opened:
            return True, used_method, None
        errors.append(f"{used_method}: {error}")

    try:
        opened = webbrowser.open(LOGIN_URL, new=2)
        if opened:
            return True, "python webbrowser", None
        errors.append("python webbrowser: webbrowser.open() 返回 False")
    except Exception as exc:
        errors.append(f"python webbrowser: {exc}")

    if not errors:
        errors.append("当前系统没有可用的浏览器启动命令")

    return False, None, "；".join(errors)


def main():
    opened, method, error = open_login_url()
    if opened:
        print("已在浏览器打开蝉镜登录页。")
        print(f"打开方式：{method}")
    else:
        print("未能自动打开浏览器，请手动访问下面的地址：")
        print(f"  {LOGIN_URL}")
        print()
        print(f"失败原因：{error}")
    print()
    print("获取 AK/SK 的方式：")
    print("1. 新用户：注册成功后，当前页面会直接展示 App ID 和 Secret Key，可点击复制按钮。")
    print("2. 老用户：登录后如果进入控制台，请在左侧菜单进入“API 密钥”页面查看或重置密钥。")
    print()
    print("拿到秘钥后请执行：")
    print("  python skills/chanjing-credentials-guard/scripts/chanjing_config.py --ak <你的app_id> --sk <你的secret_key>")
    print("设置完毕后请重新执行您之前的操作。")


if __name__ == "__main__":
    main()
