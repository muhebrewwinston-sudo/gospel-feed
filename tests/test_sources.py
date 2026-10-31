import unittest
from datetime import date
from unittest.mock import Mock, patch

import requests

from sources.bible_gateway_rss import VerseSourceError, get_verse_of_the_day
from sources.kjv_local import VERSES
from sources.kjv_local import get_verse_of_the_day as get_kjv_verse

SAMPLE_FEED = b"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <title>John 3:16</title>
    <content type="html">&lt;p&gt;For God so loved the world.&lt;sup&gt;1&lt;/sup&gt;&lt;/p&gt;</content>
  </entry>
</feed>
"""


class KjvSourceTests(unittest.TestCase):
    def test_local_source_is_deterministic(self):
        day = date(2026, 10, 31)
        self.assertEqual(get_kjv_verse(day), get_kjv_verse(day))

    def test_collection_contains_complete_entries(self):
        self.assertGreaterEqual(len(VERSES), 10)
        for text, reference in VERSES:
            self.assertTrue(text.strip())
            self.assertIn("KJV", reference)


class RssSourceTests(unittest.TestCase):
    @patch("sources.bible_gateway_rss.requests.get")
    def test_parses_official_feed_entry(self, mock_get):
        response = Mock()
        response.content = SAMPLE_FEED
        response.raise_for_status.return_value = None
        mock_get.return_value = response

        verse = get_verse_of_the_day(timeout=12)

        self.assertEqual(verse["reference"], "John 3:16")
        self.assertEqual(verse["text"], "For God so loved the world.")
        self.assertEqual(mock_get.call_args.kwargs["timeout"], 12)

    @patch("sources.bible_gateway_rss.requests.get")
    def test_empty_feed_is_rejected(self, mock_get):
        response = Mock()
        response.content = b'<feed xmlns="http://www.w3.org/2005/Atom"></feed>'
        response.raise_for_status.return_value = None
        mock_get.return_value = response

        with self.assertRaises(VerseSourceError):
            get_verse_of_the_day()

    @patch("sources.bible_gateway_rss.requests.get")
    def test_network_error_is_reported(self, mock_get):
        mock_get.side_effect = requests.Timeout("timed out")
        with self.assertRaises(VerseSourceError):
            get_verse_of_the_day()


if __name__ == "__main__":
    unittest.main()
