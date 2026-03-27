#!/usr/bin/env python3
import json
import urllib.parse
import urllib.request

API_BASE = (__import__("os").environ.get("CHANJING_OPENAPI_BASE_URL") or __import__("os").environ.get("CHANJING_API_BASE") or "https://open-api.chanjing.cc").rstrip("/")

PHOTO_RUNNING = {"Ready", "Generating", "Queued"}
PHOTO_SUCCESS = {"Success"}
PHOTO_FAILED = {"Error", "Fail"}

MOTION_RUNNING = {"Ready", "Generating", "Queued"}
MOTION_SUCCESS = {"Success"}
MOTION_FAILED = {"Error", "Fail"}

LORA_RUNNING = {"Queued", "Published", "Generating"}
LORA_SUCCESS = {"Success"}
LORA_FAILED = {"Fail"}


def api_get(token, path, query=None):
    query = query or {}
    suffix = ""
    if query:
        suffix = "?" + urllib.parse.urlencode(query)
    req = urllib.request.Request(
        f"{API_BASE}{path}{suffix}",
        headers={"access_token": token},
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    if body.get("code") != 0:
        raise RuntimeError(body.get("msg", body))
    return body.get("data")


def api_post(token, path, payload):
    req = urllib.request.Request(
        f"{API_BASE}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"access_token": token, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    if body.get("code") != 0:
        raise RuntimeError(body.get("msg", body))
    return body.get("data")


def get_photo_task(token, unique_id):
    return api_get(token, "/open/v1/aigc/photo/task", {"unique_id": unique_id})


def list_photo_tasks(token, page=1, page_size=10):
    return api_get(token, "/open/v1/aigc/photo/task/page", {"page": page, "page_size": page_size})


def get_motion_task(token, unique_id):
    return api_get(token, "/open/v1/aigc/motion/task", {"unique_id": unique_id})


def get_lora_task(token, lora_id):
    return api_get(token, "/open/v1/aigc/lora/task", {"lora_id": lora_id})


def first_output_url(data):
    urls = (data or {}).get("output_url") or []
    if isinstance(urls, list) and urls:
        return urls[0]
    return None
