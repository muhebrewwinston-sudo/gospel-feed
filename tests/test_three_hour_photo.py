import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo

from config import Settings
from three_hour import run
from utils.history import load_history


class ThreeHourPhotoTests(unittest.TestCase):
    def test_eight_slots_create_photo_captions_and_skip_duplicate_slot(self):
        with tempfile.TemporaryDirectory() as directory:
            history_path = Path(directory) / "history.json"
            settings = Settings(
                facebook_page_id="page",
                facebook_access_token="token",
                graph_api_version="v24.0",
                bible_source="kjv",
                post_hashtags="#Faith",
                max_post_length=2000,
                request_timeout=30,
                timezone="Africa/Blantyre",
                history_file=history_path,
                dry_run=False,
            )
            with patch("three_hour.generate_verse_card", side_effect=lambda text, ref, path, theme: path) as cards:
                with patch("three_hour.post_photo_to_facebook", side_effect=[f"post-{i}" for i in range(8)]) as poster:
                    for hour in (0, 3, 6, 9, 12, 15, 18, 21):
                        now = datetime(2026, 10, 31, hour, 0, tzinfo=ZoneInfo("Africa/Blantyre"))
                        self.assertEqual(run(settings, now), 0)
                    self.assertEqual(cards.call_count, 8)
                    self.assertEqual(poster.call_count, 8)
                    self.assertIn("💭 Reflection", poster.call_args.kwargs["message"])

                    now = datetime(2026, 10, 31, 21, 0, tzinfo=ZoneInfo("Africa/Blantyre"))
                    self.assertEqual(run(settings, now), 0)
                    self.assertEqual(poster.call_count, 8)

            history = load_history(history_path)
            self.assertEqual(len(history), 8)
            self.assertTrue(all(record["media"] == "photo" for record in history.values()))


if __name__ == "__main__":
    unittest.main()
