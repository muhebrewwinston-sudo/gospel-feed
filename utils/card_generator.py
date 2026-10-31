"""Generate themed 1080×1350 Bible verse cards using local assets."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
BACKGROUNDS = ROOT / "assets" / "backgrounds"
FONTS = ROOT / "assets" / "fonts"
WIDTH, HEIGHT = 1080, 1350
THEMES = {
    "peace": ("peace.webp", (190, 220, 199)),
    "guidance": ("guidance.webp", (242, 199, 112)),
    "hope": ("hope.webp", (250, 190, 104)),
    "love": ("love.webp", (238, 176, 143)),
    "strength": ("strength.webp", (228, 196, 123)),
    "rest": ("rest.webp", (178, 199, 236)),
}


def _font(filename: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / filename), size=size)


def _wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in " ".join(text.split()).split():
        candidate = f"{current} {word}".strip()
        if current and draw.textlength(candidate, font=font) > width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def _fit_verse(draw: ImageDraw.ImageDraw, text: str) -> tuple[ImageFont.FreeTypeFont, list[str], int]:
    for size in range(66, 35, -2):
        font = _font("DejaVuSerif-Bold.ttf", size)
        lines = _wrap(draw, text, font, 800)
        line_height = int(size * 1.32)
        if len(lines) * line_height <= 590:
            return font, lines, line_height
    raise ValueError("Verse is too long for the card template")


def _centered(draw: ImageDraw.ImageDraw, y: int, text: str, font: ImageFont.FreeTypeFont, fill, shadow: bool = False) -> None:
    box = draw.textbbox((0, 0), text, font=font)
    x = (WIDTH - (box[2] - box[0])) / 2
    if shadow:
        draw.text((x + 2, y + 3), text, font=font, fill=(0, 0, 0, 170))
    draw.text((x, y), text, font=font, fill=fill)


def generate_verse_card(verse_text: str, reference: str, output_path: Path, theme: str) -> Path:
    """Create a portrait PNG card and return its path."""
    if theme not in THEMES:
        raise ValueError(f"Unknown card theme: {theme}")
    if not verse_text.strip() or not reference.strip():
        raise ValueError("Verse text and reference are required")

    background_file, accent = THEMES[theme]
    with Image.open(BACKGROUNDS / background_file) as source:
        image = ImageOps.fit(
            source.convert("RGB"),
            (WIDTH, HEIGHT),
            method=Image.Resampling.LANCZOS,
        )
    image = ImageEnhance.Contrast(image).enhance(0.96).convert("RGBA")
    image = Image.alpha_composite(image, Image.new("RGBA", image.size, (3, 12, 25, 64)))

    draw = ImageDraw.Draw(image)
    verse_font, lines, line_height = _fit_verse(draw, verse_text)
    text_height = len(lines) * line_height
    panel_height = 300 + text_height
    panel_top = max(210, (HEIGHT - panel_height) // 2)
    panel_bottom = panel_top + panel_height

    panel = Image.new("RGBA", image.size, (0, 0, 0, 0))
    panel_draw = ImageDraw.Draw(panel)
    panel_draw.rounded_rectangle(
        (65, panel_top, WIDTH - 65, panel_bottom),
        radius=38,
        fill=(4, 14, 28, 190),
        outline=(*accent, 145),
        width=2,
    )
    image = Image.alpha_composite(image, panel)
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle((WIDTH // 2 - 44, panel_top + 46, WIDTH // 2 + 44, panel_top + 51), radius=2, fill=accent)
    _centered(draw, panel_top + 72, "DAILY BIBLE VERSE", _font("DejaVuSans-Bold.ttf", 27), (*accent, 255))

    y = panel_top + 145
    for line in lines:
        _centered(draw, y, line, verse_font, (252, 250, 244, 255), shadow=True)
        y += line_height

    _centered(draw, panel_bottom - 90, f"— {reference} —", _font("DejaVuSans-Bold.ttf", 30), (*accent, 255))
    _centered(draw, HEIGHT - 78, "KJV  •  DAILY ENCOURAGEMENT", _font("DejaVuSans.ttf", 22), (235, 239, 242, 235))

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(output_path, format="PNG", optimize=True)
    return output_path
