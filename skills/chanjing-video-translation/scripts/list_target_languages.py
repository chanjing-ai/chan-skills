#!/usr/bin/env python3
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _api import api_get
from _auth import get_token


def main():
    token, error = get_token()
    if error:
        raise SystemExit(error)
    print(json.dumps(api_get(token, "/open/v1/video_translation/target_languages"), ensure_ascii=False))


if __name__ == "__main__":
    main()
