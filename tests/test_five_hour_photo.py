import json
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo

from config import Settings
from five_hour import SLOT_KEY_PREFIX, run, slot_for_time
from sources.kjv_local import VERSES
from utils.history import load_history


class FiveHourPhotoTests(unittest.TestCase):
    def _settings(self, history_path, dry_run=False):
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
            dry_run=dry_run,
        )

    def test_five_slots_create_photo_captions_and_skip_duplicate_slot(self):
        with tempfile.TemporaryDirectory() as directory:
            history_path = Path(directory) / "history.json"
            settings = self._settings(history_path)
            with patch("five_hour.generate_verse_card", side_effect=lambda text, ref, path, theme: path) as cards:
                with patch("five_hour.post_photo_to_facebook", side_effect=[f"post-{i}" for i in range(5)]) as poster:
                    for hour in (3, 8, 13, 18, 23):
                        now = datetime(2026, 10, 31, hour, 0, tzinfo=ZoneInfo("Africa/Blantyre"))
                        self.assertEqual(run(settings, now), 0)
                    self.assertEqual(cards.call_count, 5)
                    self.assertEqual(poster.call_count, 5)
                    self.assertIn("💭 Reflection", poster.call_args.kwargs["message"])

                    now = datetime(2026, 10, 31, 23, 0, tzinfo=ZoneInfo("Africa/Blantyre"))
                    self.assertEqual(run(settings, now), 0)
                    self.assertEqual(poster.call_count, 5)

            history = load_history(history_path)
            self.assertEqual(len(history), 5)
            self.assertEqual(sorted(record["rotation_index"] for record in history.values()), list(range(5)))
            self.assertTrue(all(record["media"] == "photo" for record in history.values()))
            self.assertTrue(all(record["schedule"] == "five-hour" for record in history.values()))
            self.assertTrue(all(SLOT_KEY_PREFIX in key for key in history))

    def test_legacy_history_continues_with_new_passages(self):
        with tempfile.TemporaryDirectory() as directory:
            history_path = Path(directory) / "history.json"
            old_key = "2026-10-31|kjv|matthew 11:28 (kjv)|slot-6"
            history_path.write_text(json.dumps({"posted_verses": {old_key: {"reference": "Matthew 11:28 (KJV)", "slot": 6}}}))
            settings = self._settings(history_path)
            with patch("five_hour.generate_verse_card", side_effect=lambda text, ref, path, theme: path) as cards:
                with patch("five_hour.post_photo_to_facebook", return_value="new-post"):
                    now = datetime(2026, 11, 3, 3, 0, tzinfo=ZoneInfo("Africa/Blantyre"))
                    self.assertEqual(run(settings, now), 0)
            self.assertEqual(cards.call_args.args[1], VERSES[16][1])
            history = load_history(history_path)
            self.assertEqual({record["rotation_index"] for record in history.values() if "rotation_index" in record}, {16})

    def test_old_three_hour_slot_does_not_block_new_schedule(self):
        with tempfile.TemporaryDirectory() as directory:
            history_path = Path(directory) / "history.json"
            old_key = "2026-11-03|kjv|1 corinthians 13:13 (kjv)|slot-0"
            history_path.write_text(json.dumps({"posted_verses": {old_key: {"reference": "1 Corinthians 13:13 (KJV)", "slot": 0}}}))
            settings = self._settings(history_path)
            with patch("five_hour.generate_verse_card", side_effect=lambda text, ref, path, theme: path) as cards:
                with patch("five_hour.post_photo_to_facebook", return_value="new-post") as poster:
                    now = datetime(2026, 11, 3, 3, 0, tzinfo=ZoneInfo("Africa/Blantyre"))
                    self.assertEqual(run(settings, now), 0)
            self.assertEqual(cards.call_count, 1)
            self.assertEqual(poster.call_count, 1)

    def test_slot_duplicate_is_detected_even_with_another_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            history_path = Path(directory) / "history.json"
            key = f"2026-11-03|kjv|another reference|{SLOT_KEY_PREFIX}0"
            history_path.write_text(json.dumps({"posted_verses": {key: {"reference": "Another Reference", "slot": 0}}}))
            settings = self._settings(history_path)
            with patch("five_hour.generate_verse_card") as cards:
                with patch("five_hour.post_photo_to_facebook") as poster:
                    now = datetime(2026, 11, 3, 3, 0, tzinfo=ZoneInfo("Africa/Blantyre"))
                    self.assertEqual(run(settings, now), 0)
            cards.assert_not_called()
            poster.assert_not_called()

    def test_slot_boundaries_match_malawi_posting_times(self):
        timezone = ZoneInfo("Africa/Blantyre")
        expected = {0: 4, 2: 4, 3: 0, 7: 0, 8: 1, 12: 1, 13: 2, 17: 2, 18: 3, 22: 3, 23: 4}
        for hour, slot in expected.items():
            with self.subTest(hour=hour):
                self.assertEqual(slot_for_time(datetime(2026, 11, 3, hour, 0, tzinfo=timezone)), slot)

    def test_complete_rotation_has_no_repeats_before_cycle_wrap(self):
        with tempfile.TemporaryDirectory() as directory:
            history_path = Path(directory) / "history.json"
            settings = self._settings(history_path)
            start = datetime(2026, 1, 1, 3, 0, tzinfo=ZoneInfo("Africa/Blantyre"))
            with patch("five_hour.generate_verse_card", side_effect=lambda text, ref, path, theme: path):
                with patch("five_hour.post_photo_to_facebook", side_effect=[f"post-{i}" for i in range(1001)]) as poster:
                    for index in range(1001):
                        self.assertEqual(run(settings, start + timedelta(hours=5 * index)), 0)
            self.assertEqual(poster.call_count, 1001)
            history = load_history(history_path)
            ordered = sorted(history.values(), key=lambda record: record["rotation_index"])
            self.assertEqual([record["reference"] for record in ordered[:1000]], [reference for _, reference in VERSES])
            self.assertEqual(ordered[1000]["reference"], VERSES[0][1])
            self.assertEqual(ordered[1000]["rotation_index"], 1000)


if __name__ == "__main__":
    unittest.main()
