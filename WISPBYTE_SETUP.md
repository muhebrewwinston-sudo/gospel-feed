# Wispbyte setup for Bible Feed

## 1. Upload and extract

In Wispbyte, open **Server Management → Files**. Upload `gospel-feed-wispbyte.zip` and use **Unarchive**. The files must be extracted into the server root, not left inside the ZIP. If they are inside a `gospel-feed-wispbyte` folder, move the contents into the root.

Keep `requirements.txt` in the root so Wispbyte can install the dependencies.

## 2. Startup settings

Open **Startup** and set the startup command to:

```bash
python scheduler.py
```

Set these **Environment Variables**:

```text
FACEBOOK_PAGE_ID=383365871537147
FACEBOOK_ACCESS_TOKEN=your_page_token_here
FACEBOOK_GRAPH_VERSION=v24.0
POST_TIMEZONE=Africa/Blantyre
POSTER_DRY_RUN=false
POSTER_RUN_ON_STARTUP=false
POSTED_VERSES_FILE=data/posted_verses.json
POST_HASHTAGS=#BibleFeed #BibleVerse #DailyVerse #Gospel #Faith #Jesus #KJV
```

Never share the Facebook token publicly or include it in the ZIP.

## 3. Optional safe test

To test without publishing, temporarily set:

```text
POSTER_DRY_RUN=true
POSTER_RUN_ON_STARTUP=true
```

Start the server. The console should show a prepared photo post and then the next scheduled time. After the test, set `POSTER_DRY_RUN=false` and `POSTER_RUN_ON_STARTUP=false`, then restart.

## 4. Run continuously

Select **Console → Start**. Leave the server running. The scheduler posts at **03:00, 08:00, 13:00, 18:00, and 23:00 Africa/Blantyre time**. It sleeps between posts and uses `data/posted_verses.json` to avoid repeating a slot after a restart. The 1,000-passage collection provides about 200 days before the rotation cycles.

Only one live runner should be active. Disable the GitHub schedule before enabling live posting on Wispbyte.
