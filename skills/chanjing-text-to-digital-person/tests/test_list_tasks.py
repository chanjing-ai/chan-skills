import importlib.util
import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
SPEC = importlib.util.spec_from_file_location("text_to_digital_person_list_tasks", SCRIPTS / "list_tasks.py")
LIST_TASKS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LIST_TASKS)


class ListTasksTest(unittest.TestCase):
    def test_motion_kind_uses_motion_page_endpoint(self):
        with (
            patch.object(LIST_TASKS, "get_token", return_value=("token", None)),
            patch.object(LIST_TASKS, "list_motion_tasks", return_value=[]) as list_motion_tasks,
            patch.object(sys, "argv", ["list_tasks.py", "--kind", "motion", "--json"]),
            redirect_stdout(io.StringIO()),
        ):
            LIST_TASKS.main()
        list_motion_tasks.assert_called_once_with("token", page=1, page_size=10)


if __name__ == "__main__":
    unittest.main()
