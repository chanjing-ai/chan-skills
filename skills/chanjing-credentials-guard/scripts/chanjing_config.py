#!/usr/bin/env python3
"""
蝉镜凭证配置脚本。AK/SK 与 Token 均从本脚本定义的配置文件中读写。
配置文件: CONFIG_DIR/credentials.json（默认 ~/.chanjing；目录由 CHANJING_OPENAPI_CREDENTIALS_DIR 或旧名 CHANJING_CONFIG_DIR 覆盖）。
用法: python chanjing_config.py --ak <app_id> --sk <secret_key> | --status | --help
"""
import argparse
import json
import os
import sys
from pathlib import Path


def credentials_config_dir() -> Path:
    raw = os.environ.get("CHANJING_OPENAPI_CREDENTIALS_DIR") or os.environ.get("CHANJING_CONFIG_DIR")
    return Path(raw).expanduser() if raw else Path.home() / ".chanjing"


CONFIG_DIR = credentials_config_dir()
CONFIG_FILE = CONFIG_DIR / "credentials.json"
LOGIN_URL = "https://www.chanjing.cc/openapi/login"
DOC_URL = "https://doc.chanjing.cc"


def ensure_config_dir():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(CONFIG_DIR, 0o700)
    except OSError:
        pass


def read_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def write_config(data):
    ensure_config_dir()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    try:
        os.chmod(CONFIG_FILE, 0o600)
    except OSError:
        pass


def show_status():
    ensure_config_dir()
    if not CONFIG_FILE.exists():
        print("状态: 未配置")
        print()
        print("请先设置 AK/SK：")
        print("  python skills/chanjing-credentials-guard/scripts/chanjing_config.py --ak <你的app_id> --sk <你的secret_key>")
        print()
        print("获取秘钥:", LOGIN_URL)
        return 1

    data = read_config()
    has_ak = bool(data.get("app_id"))
    has_sk = bool(data.get("secret_key"))

    print("配置路径:", CONFIG_FILE)
    print("AK (app_id):", "已配置" if has_ak else "未配置")
    print("SK (secret_key):", "已配置" if has_sk else "未配置")

    if not has_ak or not has_sk:
        print()
        print("请完成 AK/SK 配置：")
        print("  python skills/chanjing-credentials-guard/scripts/chanjing_config.py --ak <你的app_id> --sk <你的secret_key>")
        print()
        print("获取秘钥:", LOGIN_URL)
        return 1

    if data.get("access_token") and data.get("expire_in") is not None:
        import time
        try:
            expire_in = int(data["expire_in"])
            now = int(time.time())
            if expire_in > now + 300:
                from datetime import datetime
                try:
                    dt = datetime.fromtimestamp(expire_in)
                    print("Token: 有效 (过期时间:", dt.strftime("%Y-%m-%d %H:%M:%S"), ")")
                except Exception:
                    print("Token: 有效 (过期时间戳:", expire_in, ")")
            else:
                print("Token: 已过期或即将过期，下次调用 API 时将自动刷新")
        except (ValueError, TypeError):
            print("Token: 已过期或即将过期，下次调用 API 时将自动刷新")
    else:
        print("Token: 未获取，下次调用 API 时将自动申请")
    return 0


def set_credentials(ak, sk):
    data = read_config()
    data["app_id"] = ak
    data["secret_key"] = sk
    write_config(data)
    print("凭证已保存到", CONFIG_FILE)
    print()
    print("验证配置: python skills/chanjing-credentials-guard/scripts/chanjing_config.py --status")


def main():
    parser = argparse.ArgumentParser(
        description="蝉镜凭证配置工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="存储位置: %s\n获取秘钥: %s\n文档: %s" % (CONFIG_FILE, LOGIN_URL, DOC_URL),
    )
    parser.add_argument("--ak", help="Access Key (app_id)")
    parser.add_argument("--sk", help="Secret Key (secret_key)")
    parser.add_argument("--status", "-s", action="store_true", help="查看配置状态")

    args = parser.parse_args()

    if args.status:
        sys.exit(show_status())

    if args.ak and args.sk:
        set_credentials(args.ak, args.sk)
        return

    if args.ak or args.sk:
        print("错误: 必须同时提供 --ak 和 --sk", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    # 默认显示状态
    sys.exit(show_status())


if __name__ == "__main__":
    main()
