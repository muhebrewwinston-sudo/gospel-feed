import tempfile
import unittest
from pathlib import Path

from PIL import Image

from sources.kjv_local import VERSES
from utils.card_generator import generate_verse_card


class CardGeneratorTests(unittest.TestCase):
    def test_generates_portrait_png_for_short_and_long_verses(self):
        with tempfile.TemporaryDirectory() as directory:
            for index, theme in ((0, "love"), (4, "hope")):
                text, reference = VERSES[index]
                output = Path(directory) / f"{theme}.png"
                generate_verse_card(text, reference, output, theme)
                self.assertTrue(output.exists())
                self.assertGreater(output.stat().st_size, 50_000)
                with Image.open(output) as image:
                    self.assertEqual(image.size, (1080, 1350))
                    self.assertEqual(image.format, "PNG")

    def test_unknown_theme_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                generate_verse_card("Text", "Reference", Path(directory) / "card.png", "unknown")


if __name__ == "__main__":
    unittest.main()
