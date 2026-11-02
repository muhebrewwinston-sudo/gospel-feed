# Bible Feed — KJV Facebook Photo Poster

Bible Feed publishes polished, locally rendered Scripture photo cards to the official Facebook Page through the Meta Graph API. The publication system is designed for long-term operation without live AI keys, image-generation charges, or scraping.

## Publication system

- **1,000 unique KJV passages**, checked against a public-domain machine-readable KJV text. Traditional `LORD` capitalization is preserved.
- **Five posts every day** at **03:00, 08:00, 13:00, 18:00, and 23:00 Africa/Blantyre**. A full 1,000-passage rotation lasts approximately **200 days**.
- **A prewritten themed reflection for every passage**. No live AI service or per-post API charge is used.
- **Six locally rendered photo-card themes** with bundled backgrounds and DejaVu fonts. Scripture is rendered as text, not generated inside an image.
- **Consistent Bible Feed branding** on every card and caption, including `#BibleFeed`.
- **Persistent monotonic rotation** in `data/posted_verses.json`. Every passage is used once before the collection cycles, and a completed slot cannot be posted again by a rerun.
- **Schedule-aware history keys** (`five-hour-slot-*`) preserve older three-hour history without letting old slot numbers block the new timetable.

The main entry point is `five_hour.py`. `scheduler.py` keeps the same poster alive continuously on Wispbyte.

## Posting schedule

GitHub Actions cron uses UTC; Malawi is UTC+2 year-round.

| Malawi time | UTC cron |
| --- | --- |
| 03:00 | `0 1 * * *` |
| 08:00 | `0 6 * * *` |
| 13:00 | `0 11 * * *` |
| 18:00 | `0 16 * * *` |
| 23:00 | `0 21 * * *` |

GitHub scheduled workflows can start late. The Wispbyte scheduler uses the same local slot boundaries and sleeps between posts.

## Local validation and dry run

Requires Python 3.10 or newer.

```bash
python -m venv .venv
source .venv/bin/activate             # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
POSTER_DRY_RUN=true python five_hour.py
```

The dry run renders a real card and prepares the caption but does **not** publish or write posting history. It does not require Facebook credentials.

For a local live post, copy `.env.example` to `.env`, add a long-lived Page Access Token, and explicitly set `POSTER_DRY_RUN=false`. Never commit `.env` or any token.

## GitHub Actions deployment

The only scheduled workflow is `.github/workflows/five-hours.yml`.

1. Push the complete project to the repository's `main` branch.
2. In **Settings → Secrets and variables → Actions**, add `FACEBOOK_PAGE_ID` and a long-lived `FACEBOOK_ACCESS_TOKEN` with the required Page publishing permission.
3. Open **Actions → Five Hour KJV Bible Verse Poster → Run workflow** and leave `dry_run` selected for a safe verification run.
4. Scheduled runs publish live after credentials are configured. Successful live runs commit the updated history file back to `main`.

Do not run Wispbyte and GitHub live posting at the same time. Keep exactly one live runner.

## Wispbyte continuous hosting

Upload and extract `gospel-feed-wispbyte.zip` into the server root. Keep `requirements.txt` at the root, then use this startup command:

```bash
python scheduler.py
```

Set the environment variables shown in `WISPBYTE_SETUP.md`, including `POSTER_DRY_RUN=false` for live operation and `POSTER_RUN_ON_STARTUP=false` for normal use. The server continues running while the owner's computer or phone is off.

Before starting Wispbyte live posting, pause the GitHub schedule. Before re-enabling GitHub, stop Wispbyte.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `FACEBOOK_PAGE_ID` | empty | Target Facebook Page ID |
| `FACEBOOK_ACCESS_TOKEN` | empty | Long-lived Page Access Token |
| `FACEBOOK_GRAPH_VERSION` | `v24.0` | Meta Graph API version |
| `POST_TIMEZONE` | `Africa/Blantyre` | Local schedule and history timezone |
| `POSTER_DRY_RUN` | `false` | Set `true` to render without publishing |
| `POSTER_RUN_ON_STARTUP` | `false` | Optional Wispbyte startup run; duplicate protection remains active |
| `POST_HASHTAGS` | Bible Feed/faith hashtags | Caption hashtags; may be blank |
| `MAX_POST_LENGTH` | `2000` | Caption safety limit |
| `REQUEST_TIMEOUT` | `30` | Graph API timeout in seconds |
| `POSTED_VERSES_FILE` | `data/posted_verses.json` | Persistent history location |

## Project structure

```text
gospel-feed/
├── .github/workflows/five-hours.yml
├── assets/backgrounds/          # Six themed local backgrounds
├── assets/fonts/                # Bundled DejaVu fonts and license
├── data/posted_verses.json      # Persistent rotation and slot history
├── data/reflections.json        # 1,000 prewritten reflections
├── facebook/poster.py           # Official Graph API photo upload
├── sources/kjv_local.py         # 1,000 exact KJV passages
├── tests/
├── utils/card_generator.py      # 1080×1350 branded card renderer
├── utils/formatter.py
├── utils/history.py
├── config.py
├── five_hour.py                 # One scheduled publication run
├── scheduler.py                 # Continuous Wispbyte scheduler
├── requirements.txt
└── WISPBYTE_SETUP.md
```

`main.py` and the RSS source remain only as legacy alternatives; they are not used by the Bible Feed schedule.

## Content rights and presentation

The KJV text is public domain. The reflections are prewritten original editorial copy bundled with the project. The card renderer uses local assets so the same design is reproducible on GitHub Actions and Wispbyte. Facebook credentials belong only in secure environment settings and must never be committed or printed.
