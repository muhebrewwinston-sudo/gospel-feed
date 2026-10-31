import os
import unittest
from unittest.mock import patch

from config import env_bool, load_settings


class ConfigTests(unittest.TestCase):
    @patch.dict(os.environ, {}, clear=True)
    def test_defaults(self):
        settings = load_settings()
        self.assertEqual(settings.bible_source, "rss")
        self.assertEqual(settings.timezone, "Africa/Blantyre")
        self.assertEqual(settings.graph_api_version, "v24.0")
        self.assertFalse(settings.dry_run)

    @patch.dict(os.environ, {"POSTER_DRY_RUN": "yes"}, clear=True)
    def test_boolean_environment_value(self):
        self.assertTrue(env_bool("POSTER_DRY_RUN"))

    @patch.dict(os.environ, {"POSTER_DRY_RUN": "perhaps"}, clear=True)
    def test_invalid_boolean_is_rejected(self):
        with self.assertRaises(ValueError):
            env_bool("POSTER_DRY_RUN")

    @patch.dict(os.environ, {"BIBLE_SOURCE": "scraper"}, clear=True)
    def test_unknown_source_is_rejected(self):
        with self.assertRaises(ValueError):
            load_settings()


if __name__ == "__main__":
    unittest.main()
