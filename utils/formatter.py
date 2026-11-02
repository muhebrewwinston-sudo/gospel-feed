"""Formatting helpers for Facebook post text."""


def format_post(
    verse_text: str,
    reference: str,
    hashtags: str = "",
    max_post_length: int = 2000,
) -> str:
    """Create a clean post and reject unexpectedly long content."""
    clean_text = " ".join(verse_text.split())
    clean_reference = " ".join(reference.split())
    clean_hashtags = " ".join(hashtags.split())

    if not clean_text or not clean_reference:
        raise ValueError("Verse text and reference are required")

    # Some RSS entries already include an outer pair of quotation marks.
    # Remove that pair so the template does not display nested outer quotes.
    if len(clean_text) >= 2 and (
        (clean_text.startswith("“") and clean_text.endswith("”"))
        or (clean_text.startswith('"') and clean_text.endswith('"'))
    ):
        clean_text = clean_text[1:-1].strip()

    post = f'📖 Bible Feed\n\n"{clean_text}"\n\n— {clean_reference}'
    if clean_hashtags:
        post = f"{post}\n\n{clean_hashtags}"

    if len(post) > max_post_length:
        raise ValueError(
            f"Formatted post is {len(post)} characters; "
            f"the configured limit is {max_post_length}"
        )

    return post
