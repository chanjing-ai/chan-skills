import argparse
import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
SPEC = importlib.util.spec_from_file_location("video_translation_create_task", SCRIPTS / "create_task.py")
CREATE_TASK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CREATE_TASK)


class CreateTaskPayloadTest(unittest.TestCase):
    def test_builds_minimal_payload(self):
        args = argparse.Namespace(
            body_file=None,
            body_json=None,
            video_id=None,
            file_id="file-1",
            title="demo",
            target_language=["en", "ja"],
            audio_id="voice-1",
            need_lip_sync=True,
            need_dynamic_duration=False,
            need_subtitle=True,
        )
        self.assertEqual(
            CREATE_TASK.build_payload(args),
            {
                "source": {"file_id": "file-1", "title": "demo"},
                "target_languages": ["en", "ja"],
                "audio_id": "voice-1",
                "need_lip_sync": True,
                "need_subtitle": True,
            },
        )


if __name__ == "__main__":
    unittest.main()
