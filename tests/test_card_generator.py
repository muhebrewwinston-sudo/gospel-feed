import tempfile
import unittest
from pathlib import Path

from PIL import Image

from sources.kjv_local import VERSES
from utils.card_generator import BRAND_NAME, THEMES, generate_verse_card


class CardGeneratorTests(unittest.TestCase):
    def test_generates_portrait_png_for_short_and_long_verses(self):
        longest_text, longest_reference = max(VERSES, key=lambda item: len(item[0]))
        with tempfile.TemporaryDirectory() as directory:
            samples = [(VERSES[0][0], VERSES[0][1], "love"), (longest_text, longest_reference, "hope")]
            for index, (text, reference, theme) in enumerate(samples):
                output = Path(directory) / f"card-{index}.png"
                generate_verse_card(text, reference, output, theme)
                self.assertTrue(output.exists())
                self.assertGreater(output.stat().st_size, 50_000)
                with Image.open(output) as image:
                    self.assertEqual(image.size, (1080, 1350))
                    self.assertEqual(image.format, "PNG")

    def test_every_theme_renders_the_longest_passage(self):
        text, reference = max(VERSES, key=lambda item: len(item[0]))
        with tempfile.TemporaryDirectory() as directory:
            for theme in THEMES:
                with self.subTest(theme=theme):
                    output = Path(directory) / f"{theme}.png"
                    generate_verse_card(text, reference, output, theme)
                    self.assertGreater(output.stat().st_size, 50_000)

    def test_brand_name_is_consistent(self):
        self.assertEqual(BRAND_NAME, "BIBLE FEED")

    def test_unknown_theme_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                generate_verse_card("Text", "Reference", Path(directory) / "card.png", "unknown")


if __name__ == "__main__":
    unittest.main()
