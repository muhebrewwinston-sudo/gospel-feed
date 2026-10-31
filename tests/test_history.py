import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from utils.history import (
    HistoryError,
    load_history,
    make_verse_key,
    save_history,
)


class HistoryTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.path = Path(self.temporary_directory.name) / "data" / "history.json"

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_missing_file_returns_empty_history(self):
        self.assertEqual(load_history(self.path), {})

    def test_save_and_reload_history(self):
        history = {"key": {"post_id": "123"}}
        save_history(self.path, history)
        self.assertEqual(load_history(self.path), history)
        self.assertFalse(self.path.with_name(f"{self.path.name}.tmp").exists())

    def test_legacy_list_format_is_accepted(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text(json.dumps(["old-key"]), encoding="utf-8")
        self.assertEqual(load_history(self.path), {"old-key": {}})

    def test_corrupt_history_fails_closed(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text("not json", encoding="utf-8")
        with self.assertRaises(HistoryError):
            load_history(self.path)

    def test_verse_key_normalizes_reference(self):
        first = make_verse_key(date(2026, 10, 31), "kjv", "John   3:16 (KJV)")
        second = make_verse_key(date(2026, 10, 31), "kjv", "john 3:16 (kjv)")
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
