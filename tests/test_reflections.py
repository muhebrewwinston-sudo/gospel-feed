import json
import unittest
from pathlib import Path

from sources.kjv_local import VERSES
from utils.card_generator import THEMES


class ReflectionTests(unittest.TestCase):
    def test_every_verse_has_a_reflection_and_valid_theme(self):
        path = Path(__file__).resolve().parents[1] / "data" / "reflections.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        references = {reference for _, reference in VERSES}
        self.assertEqual(set(data), references)
        for entry in data.values():
            self.assertIn(entry["theme"], THEMES)
            self.assertGreaterEqual(len(entry["reflection"]), 60)
            self.assertLessEqual(len(entry["reflection"]), 300)


if __name__ == "__main__":
    unittest.main()
