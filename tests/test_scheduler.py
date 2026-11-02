import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

from scheduler import SLOT_HOURS, next_slot


class SchedulerTests(unittest.TestCase):
    def test_next_slot_uses_five_hour_boundaries(self):
        timezone = ZoneInfo("Africa/Blantyre")
        cases = [
            ((2026, 10, 31, 2, 59), (2026, 10, 31, 3, 0)),
            ((2026, 10, 31, 3, 0), (2026, 10, 31, 8, 0)),
            ((2026, 10, 31, 7, 59), (2026, 10, 31, 8, 0)),
            ((2026, 10, 31, 8, 0), (2026, 10, 31, 13, 0)),
            ((2026, 10, 31, 13, 0), (2026, 10, 31, 18, 0)),
            ((2026, 10, 31, 18, 0), (2026, 10, 31, 23, 0)),
            ((2026, 10, 31, 23, 0), (2026, 11, 1, 3, 0)),
            ((2026, 10, 31, 23, 59), (2026, 11, 1, 3, 0)),
        ]
        for current, expected in cases:
            with self.subTest(current=current):
                self.assertEqual(next_slot(datetime(*current, tzinfo=timezone)), datetime(*expected, tzinfo=timezone))

    def test_slot_hours_are_the_five_requested_local_times(self):
        self.assertEqual(SLOT_HOURS, (3, 8, 13, 18, 23))


if __name__ == "__main__":
    unittest.main()
