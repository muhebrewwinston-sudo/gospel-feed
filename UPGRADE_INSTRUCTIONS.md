# Free photo upgrade instructions

This package upgrades the existing five-hour KJV bot to post designed verse-card photos with prewritten AI reflections. It does not require an AI API key, a Render server, or any workflow changes.

## Install on GitHub

1. Extract `gospel-feed-photo-upgrade.zip`.
2. Open the gospel-feed repository on GitHub and choose **Add file → Upload files**.
3. Upload **all extracted files and folders**, preserving their paths. Uploading a file with the same name and path replaces the old version.
4. Commit the changes to `main`.
5. Open **Actions → Five Hour KJV Bible Verse Poster → Run workflow** and leave **Preview only** enabled for the first test.
6. After a successful dry run, the next scheduled live run will use photo posts automatically.

## Package contents

- `five_hour.py` — five-hour rotation, reflections, card creation, and photo publishing.
- `facebook/poster.py` — adds official Page photo uploads.
- `utils/card_generator.py` — local 1080×1350 card designer.
- `data/reflections.json` — sixteen prewritten AI reflections and theme assignments.
- `assets/` — six themed backgrounds and licensed DejaVu fonts.
- `requirements.txt` — adds Pillow.
- `tests/` — adds photo, reflection, and card tests.

Do not upload any Facebook token with this package. Keep using the Page token already stored in GitHub Secrets.
