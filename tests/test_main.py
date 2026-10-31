import tempfile
import unittest
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo

from config import Settings
from facebook.poster import FacebookPostError
from main import run
from utils.history import load_history


class MainTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.history_path = Path(self.temporary_directory.name) / "posted.json"
        self.settings = Settings(
            facebook_page_id="page",
            facebook_access_token="token",
            graph_api_version="v24.0",
            bible_source="kjv",
            post_hashtags="#Faith",
            max_post_length=2000,
            request_timeout=30,
            timezone="Africa/Blantyre",
            history_file=self.history_path,
            dry_run=False,
        )
        self.now = datetime(2026, 10, 31, 8, 0, tzinfo=ZoneInfo("Africa/Blantyre"))

    def tearDown(self):
        self.temporary_directory.cleanup()

    @patch("main.post_to_facebook")
    def test_dry_run_neither_posts_nor_writes_history(self, mock_post):
        result = run(replace(self.settings, dry_run=True), now=self.now)
        self.assertEqual(result, 0)
        mock_post.assert_not_called()
        self.assertFalse(self.history_path.exists())

    @patch("main.post_to_facebook", return_value="post-123")
    def test_success_is_recorded_and_second_run_is_skipped(self, mock_post):
        first_result = run(self.settings, now=self.now)
        second_result = run(self.settings, now=self.now)

        self.assertEqual(first_result, 0)
        self.assertEqual(second_result, 0)
        self.assertEqual(mock_post.call_count, 1)
        history = load_history(self.history_path)
        self.assertEqual(len(history), 1)
        self.assertEqual(next(iter(history.values()))["post_id"], "post-123")

    @patch("main.post_to_facebook", side_effect=FacebookPostError("failed"))
    def test_failed_post_is_not_recorded(self, mock_post):
        result = run(self.settings, now=self.now)
        self.assertEqual(result, 1)
        self.assertFalse(self.history_path.exists())

    @patch("main.get_verse_of_the_day")
    def test_missing_live_credentials_fail_before_fetching(self, mock_source):
        settings = replace(
            self.settings,
            facebook_page_id="",
            facebook_access_token="",
        )
        result = run(settings, now=self.now)
        self.assertEqual(result, 2)
        mock_source.assert_not_called()

    @patch("main.post_to_facebook")
    def test_corrupt_history_prevents_a_duplicate_post(self, mock_post):
        self.history_path.write_text("broken", encoding="utf-8")
        result = run(self.settings, now=self.now)
        self.assertEqual(result, 1)
        mock_post.assert_not_called()


if __name__ == "__main__":
    unittest.main()
