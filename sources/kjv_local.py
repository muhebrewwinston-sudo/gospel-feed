"""A small, deterministic collection of public-domain KJV verses.

This source needs no network connection. Add more carefully verified KJV passages
if you want a larger local rotation.
"""

from __future__ import annotations

from datetime import date

VERSES: tuple[tuple[str, str], ...] = (
    (
        "For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life.",
        "John 3:16 (KJV)",
    ),
    ("The LORD is my shepherd; I shall not want.", "Psalm 23:1 (KJV)"),
    (
        "Trust in the LORD with all thine heart; and lean not unto thine own understanding.",
        "Proverbs 3:5 (KJV)",
    ),
    (
        "I can do all things through Christ which strengtheneth me.",
        "Philippians 4:13 (KJV)",
    ),
    (
        "For I know the thoughts that I think toward you, saith the LORD, thoughts of peace, and not of evil, to give you an expected end.",
        "Jeremiah 29:11 (KJV)",
    ),
    (
        "And we know that all things work together for good to them that love God, to them who are the called according to his purpose.",
        "Romans 8:28 (KJV)",
    ),
    (
        "Come unto me, all ye that labour and are heavy laden, and I will give you rest.",
        "Matthew 11:28 (KJV)",
    ),
    (
        "God is our refuge and strength, a very present help in trouble.",
        "Psalm 46:1 (KJV)",
    ),
    (
        "And now abideth faith, hope, charity, these three; but the greatest of these is charity.",
        "1 Corinthians 13:13 (KJV)",
    ),
    (
        "Thy word is a lamp unto my feet, and a light unto my path.",
        "Psalm 119:105 (KJV)",
    ),
    (
        "Jesus saith unto him, I am the way, the truth, and the life: no man cometh unto the Father, but by me.",
        "John 14:6 (KJV)",
    ),
    (
        "For God hath not given us the spirit of fear; but of power, and of love, and of a sound mind.",
        "2 Timothy 1:7 (KJV)",
    ),
    (
        "The LORD is my light and my salvation; whom shall I fear? the LORD is the strength of my life; of whom shall I be afraid?",
        "Psalm 27:1 (KJV)",
    ),
    (
        "Be careful for nothing; but in every thing by prayer and supplication with thanksgiving let your requests be made known unto God.",
        "Philippians 4:6 (KJV)",
    ),
    (
        "And the peace of God, which passeth all understanding, shall keep your hearts and minds through Christ Jesus.",
        "Philippians 4:7 (KJV)",
    ),
    (
        "This is the day which the LORD hath made; we will rejoice and be glad in it.",
        "Psalm 118:24 (KJV)",
    ),
)


def get_verse_of_the_day(day: date | None = None) -> dict[str, str]:
    selected_day = day or date.today()
    text, reference = VERSES[selected_day.toordinal() % len(VERSES)]
    return {"text": text, "reference": reference}
