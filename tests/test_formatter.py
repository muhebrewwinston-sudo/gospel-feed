import unittest

from utils.formatter import format_post


class FormatterTests(unittest.TestCase):
    def test_formats_reference_text_and_hashtags(self):
        post = format_post("The LORD is my shepherd.", "Psalm 23:1", "#Faith #KJV")
        self.assertIn('"The LORD is my shepherd."', post)
        self.assertIn("— Psalm 23:1", post)
        self.assertTrue(post.endswith("#Faith #KJV"))

    def test_blank_hashtags_are_omitted(self):
        post = format_post("Text", "Reference", "")
        self.assertFalse(post.endswith("\n\n"))

    def test_existing_outer_quotes_are_not_duplicated(self):
        post = format_post("“For it is by grace.”", "Ephesians 2:8")
        self.assertIn('\n\n"For it is by grace."\n\n', post)
        self.assertNotIn('"“For it is by grace.”"', post)

    def test_missing_verse_is_rejected(self):
        with self.assertRaises(ValueError):
            format_post("", "Reference")

    def test_configured_length_limit_is_enforced(self):
        with self.assertRaises(ValueError):
            format_post("A long verse", "Reference", max_post_length=10)


if __name__ == "__main__":
    unittest.main()
