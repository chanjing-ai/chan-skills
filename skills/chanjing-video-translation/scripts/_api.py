#!/usr/bin/env python3
import json
import os
import urllib.parse
import urllib.request

API_BASE = (os.environ.get("CHANJING_OPENAPI_BASE_URL") or os.environ.get("CHANJING_API_BASE") or "https://open-api.chanjing.cc").rstrip("/")


def request(token, method, path, payload=None, query=None):
    suffix = "?" + urllib.parse.urlencode(query, doseq=True) if query else ""
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"access_token": token}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(API_BASE + path + suffix, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as response:
        body = json.loads(response.read().decode("utf-8"))
    if body.get("code") != 0:
        raise RuntimeError(body.get("msg", body))
    return body.get("data")


def api_get(token, path, query=None):
    return request(token, "GET", path, query=query)


def api_post(token, path, payload):
    return request(token, "POST", path, payload=payload)
