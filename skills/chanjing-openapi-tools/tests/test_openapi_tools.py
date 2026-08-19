import argparse
import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
SPEC = importlib.util.spec_from_file_location("openapi_tools", SCRIPTS / "openapi_tools.py")
OPENAPI_TOOLS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(OPENAPI_TOOLS)


class OpenAPIToolsTest(unittest.TestCase):
    def test_tag_list_query(self):
        args = argparse.Namespace(command="tag-list", business_type=[1, 2])
        with patch.object(OPENAPI_TOOLS, "api_get", return_value={"ok": True}) as api_get:
            self.assertEqual(OPENAPI_TOOLS.invoke(args, "token"), {"ok": True})
        api_get.assert_called_once_with("token", "/open/v1/tag_list", {"business_type": [1, 2]})

    def test_consume_detail_payload(self):
        args = argparse.Namespace(
            command="consume-detail",
            start_time="2026-08-01 00:00:00",
            end_time="2026-08-02 00:00:00",
            consume_type="video",
            page=2,
            page_size=20,
        )
        with patch.object(OPENAPI_TOOLS, "api_post", return_value={"ok": True}) as api_post:
            self.assertEqual(OPENAPI_TOOLS.invoke(args, "token"), {"ok": True})
        api_post.assert_called_once_with(
            "token",
            "/open/v1/consume_detail",
            {
                "start_time": "2026-08-01 00:00:00",
                "end_time": "2026-08-02 00:00:00",
                "consume_type": "video",
                "page": 2,
                "page_size": 20,
            },
        )

    def test_file_detail_query(self):
        args = argparse.Namespace(command="file-detail", id="file-1")
        with patch.object(OPENAPI_TOOLS, "api_get", return_value={"id": "file-1"}) as api_get:
            self.assertEqual(OPENAPI_TOOLS.invoke(args, "token"), {"id": "file-1"})
        api_get.assert_called_once_with("token", "/open/v1/common/file_detail", {"id": "file-1"})


if __name__ == "__main__":
    unittest.main()
