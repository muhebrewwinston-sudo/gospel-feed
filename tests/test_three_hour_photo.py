import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo

from config import Settings
from sources.kjv_local import VERSES
from three_hour import run
from utils.history import load_history


class ThreeHourPhotoTests(unittest.TestCase):
    def _settings(self, history_path):
        return Settings(
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

    def test_eight_slots_create_photo_captions_and_skip_duplicate_slot(self):
        with tempfile.TemporaryDirectory() as directory:
            history_path = Path(directory) / "history.json"
            settings = self._settings(history_path)
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
            self.assertEqual(sorted(record["rotation_index"] for record in history.values()), list(range(8)))
            self.assertTrue(all(record["media"] == "photo" for record in history.values()))

    def test_legacy_history_continues_with_new_passages(self):
        with tempfile.TemporaryDirectory() as directory:
            history_path = Path(directory) / "history.json"
            old_key = "2026-10-31|kjv|matthew 11:28 (kjv)|slot-6"
            history_path.write_text(json.dumps({"posted_verses": {old_key: {"reference": "Matthew 11:28 (KJV)", "slot": 6}}}))
            settings = self._settings(history_path)
            with patch("three_hour.generate_verse_card", side_effect=lambda text, ref, path, theme: path) as cards:
                with patch("three_hour.post_photo_to_facebook", return_value="new-post"):
                    now = datetime(2026, 11, 3, 0, 0, tzinfo=ZoneInfo("Africa/Blantyre"))
                    self.assertEqual(run(settings, now), 0)
            self.assertEqual(cards.call_args.args[1], VERSES[16][1])
            history = load_history(history_path)
            self.assertEqual({record["rotation_index"] for record in history.values() if "rotation_index" in record}, {16})

    def test_slot_duplicate_is_detected_even_with_another_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            history_path = Path(directory) / "history.json"
            key = "2026-11-03|kjv|another reference|slot-0"
            history_path.write_text(json.dumps({"posted_verses": {key: {"reference": "Another Reference", "slot": 0}}}))
            settings = self._settings(history_path)
            with patch("three_hour.generate_verse_card") as cards:
                with patch("three_hour.post_photo_to_facebook") as poster:
                    now = datetime(2026, 11, 3, 0, 0, tzinfo=ZoneInfo("Africa/Blantyre"))
                    self.assertEqual(run(settings, now), 0)
            cards.assert_not_called()
            poster.assert_not_called()


if __name__ == "__main__":
    unittest.main()
