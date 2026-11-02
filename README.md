# Gospel Feed — Daily Bible Verse Poster

Posts one daily Bible verse to a Facebook Page using either:

- **Bible Gateway's official Verse of the Day Atom feed** (`rss`, the default), or
- **A small built-in public-domain KJV rotation** (`kjv`), which also works offline.

Publishing uses the official Facebook Graph API. The project does not scrape Bible websites.

## Three-hour photo mode

`three_hour.py` creates 1080×1350 portrait verse cards and uploads them through the Facebook Page photos API. It includes:

- The same exact public-domain KJV rotation every three hours at 00:00, 03:00, 06:00, 09:00, 12:00, 15:00, 18:00, and 21:00 Malawi time.
- Eighty prewritten AI reflections—no live AI API key or ongoing AI charges.
- A persistent rotation index that uses every passage once before cycling, rather than restarting every two days.
- Six themed background images and bundled DejaVu fonts for consistent cards on GitHub Actions.
- Local image generation with Pillow, so scripture text is rendered accurately rather than generated inside an AI image.

The `three-hours.yml` and `live-now.yml` workflows use this entry point. Run the test suite with `python -m unittest discover -s tests -v`.

## Safety defaults

- `python main.py --dry-run --source kjv` previews a post without credentials, network access, or Facebook publishing.
- Manual GitHub Actions runs default to dry-run mode.
- `data/posted_verses.json` records successful live posts and prevents same-day duplicate reruns.
- Corrupt history stops the live poster instead of risking a duplicate.
- Secrets are read from `.env` locally or GitHub Actions secrets; neither real tokens nor Page credentials belong in committed files.

## Project structure

```text
gospel-feed/
├── .github/workflows/daily-post.yml
├── data/posted_verses.json
├── facebook/poster.py
├── sources/
│   ├── bible_gateway_rss.py
│   └── kjv_local.py
├── tests/
├── utils/
│   ├── formatter.py
│   ├── history.py
│   └── logger.py
├── .env.example
├── .gitignore
├── config.py
├── main.py
├── requirements.txt
└── README.md
```

## 1. Local setup

Requires Python 3.10 or newer (the workflow uses Python 3.11).

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # Windows: copy .env.example .env
```

Edit `.env` and add your Page ID and a **long-lived Page Access Token**. Keep `POSTER_DRY_RUN=true` until you are ready to publish.

Run the test suite and an offline preview:

```bash
python -m unittest discover -s tests -v
python main.py --dry-run --source kjv
```

To preview the RSS source, run `python main.py --dry-run --source rss`.

For a real local post, set `POSTER_DRY_RUN=false` in `.env` and run `python main.py`. **That publishes to the configured Facebook Page.**

## 2. Facebook credentials

Create or use a Meta developer app with access to your Page, then obtain a Page Access Token with the permissions required for publishing, including `pages_manage_posts`. Meta's app-review and access requirements can vary by app and Page.

A token that expires in about an hour is short-lived and is not suitable for a daily scheduled job. Generate or exchange it for a long-lived Page token according to Meta's current token documentation. If a token has been exposed publicly, revoke/rotate it before use.

Optional environment settings:

| Variable | Default | Purpose |
| --- | --- | --- |
| `FACEBOOK_GRAPH_VERSION` | `v24.0` | Graph API version; update as Meta versions change |
| `BIBLE_SOURCE` | `rss` | `rss` or `kjv` |
| `POST_TIMEZONE` | `Africa/Blantyre` | Timezone used for daily duplicate keys |
| `POSTER_DRY_RUN` | `false` | Set `true` to prevent publishing |
| `POST_HASHTAGS` | Bible/faith hashtags | Post hashtags; may be blank |
| `MAX_POST_LENGTH` | `2000` | Safety limit for formatted text |
| `REQUEST_TIMEOUT` | `30` | HTTP timeout in seconds |
| `POSTED_VERSES_FILE` | `data/posted_verses.json` | Persistent history location |

## 3. Automatic posting with GitHub Actions

The included workflow runs daily at **06:00 UTC / 08:00 Malawi time**. Scheduled workflows run from the repository's default branch and can sometimes start late.

1. Push this project, including `.github/workflows/daily-post.yml`, to GitHub.
2. Open **Settings → Secrets and variables → Actions**.
3. Under **Secrets**, add:
   - `FACEBOOK_PAGE_ID`
   - `FACEBOOK_ACCESS_TOKEN` — use the long-lived Page token.
4. Optional: under **Variables**, add `BIBLE_SOURCE=kjv`, a different `FACEBOOK_GRAPH_VERSION`, or other supported settings.
5. Open **Actions → Daily Bible Verse Poster → Run workflow**. Leave `dry_run` selected to preview safely.
6. For an explicit live test, run the workflow again with `dry_run` cleared. **This publishes a real post.** Scheduled runs are live automatically once credentials are configured.

After a successful live post, the workflow commits the updated history file back to the repository. The workflow requests `contents: write`; if the default branch is protected, allow GitHub Actions to push or adjust the branch rules. Do not delete or rewrite the history file between runs.

To change the schedule, edit the cron expression in `.github/workflows/daily-post.yml`. Cron uses UTC.

## Sources and content rights

The RSS option makes one request to the official feed per run; it does not repeatedly scrape full Bible pages. You are still responsible for complying with the source's terms and any translation copyright requirements. For the simplest rights posture, use the public-domain KJV source and add your own original reflections. The included KJV collection is intentionally small; extend it only with carefully verified public-domain text.
