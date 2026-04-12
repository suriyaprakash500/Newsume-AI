# Newsume AI

**An AI that reads your resume and delivers personalized news**

An Android app + Python backend that reads your resume, extracts your skills and experience, and delivers daily personalized career-relevant tech news — with AI-powered career impact cards, skill-gap analysis, and a 2-minute daily digest.

---

## Key Features

- **Resume upload + re-upload** with AI-powered skill extraction (Groq LLama 3.3)
- **User-editable profile** — add/remove skills, certifications, keywords after extraction
- **12 news sources** (11 completely free) — Hacker News, DEV Community, freeCodeCamp, Google Developers Blog, DZone, Wired, Android Authority, TechCrunch, InfoQ, GitHub Blog, NewsAPI
- **Career impact cards** per article — why it matters, who should care, concrete next action
- **Daily 2-minute digest** — top 5 bullets + 1 recommended action
- **AI skill-gap report** — missing skills vs market trends, resume improvement suggestions
- **Personalization controls** — preferred/blocked topics, seniority level (student → lead)
- **India relevance layer** — UPI/fintech, ONDC, Indian startups, GCC hiring, city-level demand
- **Unread-only feed** — 10 per page, offset pagination, refresh shows next unseen batch
- **Bookmarks + notes** for saving important articles
- **Daily 9 AM automated fetch** + push notifications with quiet hours and daily dedup
- **Retention metrics** — 7-day activity tracking (digest opens, article clicks, bookmarks)
- **Source trust scoring** and cross-source deduplication
- **Offline caching** via Room DB on Android

---

## Project Structure

```
Resume_news_updater/
├── backend/                   # Python FastAPI backend
│   ├── api/                   # HTTP routes
│   │   ├── routes_resume.py       # Upload, profile GET/PUT, FCM token
│   │   ├── routes_news.py         # Unread feed, refresh, digest, mark-read
│   │   ├── routes_bookmarks.py    # Bookmark CRUD
│   │   └── routes_preferences.py  # Topics, seniority, metrics, skill-gap
│   ├── services/              # Business logic
│   │   ├── source_aggregator.py     # Multi-source orchestrator + dedup
│   │   ├── hn_fetcher.py           # Hacker News Firebase + Algolia
│   │   ├── rss_fetcher.py          # 9 RSS feed sources
│   │   ├── news_fetcher.py         # NewsAPI integration
│   │   ├── career_impact_service.py # AI career cards + daily digest (batched)
│   │   ├── personalization_service.py # Topic/seniority filtering
│   │   ├── skill_gap_service.py     # AI skill-gap analysis
│   │   ├── news_ranker.py          # Rank + enrich + personalize pipeline
│   │   ├── skill_extractor.py      # Gemini resume parsing
│   │   ├── resume_parser.py        # Upload orchestration
│   │   ├── scheduler_service.py    # Daily 9 AM cron job
│   │   └── notification_service.py # Firebase push + quiet hours + dedup
│   ├── repositories/          # Database CRUD
│   │   ├── user_profile_repo.py
│   │   ├── news_repo.py
│   │   ├── bookmark_repo.py
│   │   └── metrics_repo.py
│   ├── models/                # SQLAlchemy ORM models
│   │   ├── user_profile.py
│   │   ├── news_article.py
│   │   ├── bookmark.py
│   │   └── metrics.py
│   ├── utils/                 # Shared helpers
│   │   ├── gemini_client.py       # Async Gemini singleton + retry + validation
│   │   ├── text_parser.py         # PDF/DOCX text extraction
│   │   ├── india_context.py       # India relevance boosting
│   │   └── relevance_scorer.py    # Scoring formula
│   ├── config/
│   │   ├── settings.py            # Pydantic-Settings env config
│   │   └── sources.py             # Source registry + trust scores
│   ├── database.py
│   ├── main.py
│   ├── Dockerfile
│   └── docker-compose.yml
├── android/                   # Native Kotlin Android app (Jetpack Compose)
│   └── app/src/main/java/com/resumenews/app/
│       ├── data/              # Room DB, Retrofit, Repositories
│       ├── viewmodel/         # ResumeViewModel, NewsViewModel
│       ├── ui/                # 4 screens + navigation + theme
│       └── worker/            # Background sync + notifications
├── IMPLEMENTATION.md          # Detailed implementation plan & status
└── README.md
```

---

## Prerequisites

| Tool | Min Version | Purpose |
|------|-------------|---------|
| Python | 3.11+ | Backend |
| JDK | 17+ | Android build |
| Android SDK | API 34 | Android build (CLI or Android Studio) |
| Docker (optional) | 24+ | Run backend in container |

---

## Quick Start — Backend

```bash
cd backend

# 1. Create env file
cp .env.example .env
# Edit .env — add your API keys (see "API Keys" section below)

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
python main.py
```

Backend starts at `http://localhost:8000`. Swagger docs at `http://localhost:8000/docs`.

### Docker alternative

```bash
cd backend
cp .env.example .env   # edit with your keys
docker compose up --build -d
```

---

## Quick Start — Android

```bash
cd android

# 1. Generate the Gradle wrapper (one-time, requires Gradle installed globally)
gradle wrapper

# 2. Build debug APK (needs Android SDK + JDK 17)
gradlew.bat assembleDebug      # Windows
./gradlew assembleDebug         # Linux/Mac

# APK at: app/build/outputs/apk/debug/app-debug.apk
```

> **Backend URL**: By default the app connects to `http://10.0.2.2:8000` (Android emulator -> host).
> For a physical device, change `BACKEND_URL` in `app/build.gradle.kts` to your machine's local IP.

> **Android SDK without Studio**: Install command-line tools from
> https://developer.android.com/studio#command-line-tools-only
> Then run: `sdkmanager "platforms;android-34" "build-tools;34.0.0"`

---

## API Keys

Add these to `backend/.env`:

| Key | Where to get | Required? |
|-----|-------------|-----------|
| `GROQ_API_KEY` | https://console.groq.com/keys | Optional — fallback extraction works without it |
| `NEWS_API_KEY` | https://newsapi.org (free: 100 req/day) | Optional — HN + RSS work without it |
| `FCM_SERVER_KEY` | Firebase Console -> Cloud Messaging -> Server Key | Optional — for push notifications only |

All other settings have sensible defaults (SQLite DB, 9 AM IST schedule, Groq llama-3.3-70b-versatile model). See `backend/.env.example` for the full list.

---

## News Sources

| Source | Type | Auth? | Trust Score |
|--------|------|-------|-------------|
| Hacker News (Firebase) | API | No key | 0.9 |
| Hacker News (Algolia) | Search API | No key | 0.9 |
| DEV Community | RSS | No key | 0.75 |
| freeCodeCamp | RSS | No key | 0.8 |
| Google Developers Blog | RSS | No key | 0.85 |
| DZone | RSS | No key | 0.7 |
| Wired | RSS | No key | 0.75 |
| Android Authority | RSS | No key | 0.75 |
| TechCrunch | RSS | No key | 0.8 |
| InfoQ | RSS | No key | 0.85 |
| GitHub Blog | RSS | No key | 0.85 |
| NewsAPI | Key API | API key | 0.7 |

12 total sources. 11 are completely free (no API key needed). NewsAPI requires a free-tier key.

---

## API Endpoints

### Resume
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/resume/upload` | Upload resume (PDF/DOCX) |
| GET | `/resume/profile/{device_id}` | Get extracted profile |
| PUT | `/resume/profile/{device_id}` | Edit profile (skills, keywords, etc.) |
| POST | `/resume/fcm-token` | Register FCM push token |

### News
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/news/{device_id}` | Unread articles (10/page, offset pagination) |
| GET | `/news/{device_id}/all` | All articles (offset pagination) |
| POST | `/news/{device_id}/refresh` | Fetch + rank + personalize from all sources |
| POST | `/news/{device_id}/mark-read` | Mark articles as read |
| GET | `/news/{device_id}/digest` | Daily career digest (5 bullets + action) |

### Bookmarks
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/bookmarks/{device_id}` | Add bookmark with optional note |
| DELETE | `/bookmarks/{device_id}/{article_id}` | Remove bookmark |
| GET | `/bookmarks/{device_id}` | List all bookmarks |

### Preferences & Intelligence
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/preferences/topics` | List available topics & seniority levels |
| GET | `/preferences/{device_id}` | Get user preference settings |
| PUT | `/preferences/{device_id}` | Update topics, seniority, notification settings, quiet hours |
| POST | `/preferences/{device_id}/track` | Log user events for retention metrics |
| GET | `/preferences/{device_id}/metrics` | 7-day retention stats |
| GET | `/preferences/{device_id}/skill-gap` | AI skill-gap report |

### System
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Health check |

19 endpoints total.

---

## How It Works

1. **Upload resume** (PDF or DOCX) via the Android app.
2. **Backend parses** using Gemini AI to extract skills, certifications, experience, education, keywords. Falls back to regex + keyword matching if no API key.
3. **User can edit** extracted profile — add/remove skills, certifications, keywords, then save.
4. **Set preferences** — choose preferred topics (AI, backend, cloud, etc.), block topics, set seniority level.
5. **Daily at 9 AM IST**, backend aggregates from 12 sources, deduplicates, ranks by `(skill_match × 0.6) + (source_trust × 0.25) + (india_boost × 0.15)`, and applies topic/seniority personalization.
6. **Career impact cards** are generated for top 5 articles via batched Gemini call (why it matters, next action).
7. **Push notification** sent (respects quiet hours 10 PM–7 AM, max 1/day per device).
8. **Android syncs** unread articles (10 per page); refresh shows next unseen batch.
9. **Digest tab** shows a 2-minute career briefing with top 5 bullets and one recommended action.
10. **Skill-gap report** compares your skills against trending article topics, suggests what to learn next.
11. **Bookmarks** let users save articles with notes for later reference.

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | (empty) | Groq API key |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Groq model name |
| `NEWS_API_KEY` | (empty) | NewsAPI.org key |
| `FCM_SERVER_KEY` | (empty) | FCM legacy server key for push notifications |
| `DATABASE_URL` | `sqlite:///./resume_news.db` | SQLAlchemy DB URL |
| `SCHEDULER_TIMEZONE` | `Asia/Kolkata` | Timezone for daily job |
| `DAILY_FETCH_HOUR` | `9` | Hour to run daily news fetch |
| `DAILY_FETCH_MINUTE` | `0` | Minute to run daily news fetch |
| `HOST` | `0.0.0.0` | Server bind host |
| `PORT` | `8000` | Server bind port |

---

## Sharing to Another Laptop

1. Copy the entire `Resume_news_updater` folder.
2. Ensure Python 3.11+ and JDK 17+ are installed.
3. `cd backend && pip install -r requirements.txt`
4. Create `backend/.env` with your API keys (copy from `.env.example`).
5. `python main.py` to start the backend.
6. Install Gradle globally, then `cd android && gradle wrapper && gradlew.bat assembleDebug`.
7. Install APK on device/emulator.

---

## Detailed Implementation Plan

See [IMPLEMENTATION.md](IMPLEMENTATION.md) for the full phase-by-phase implementation plan, architecture details, and current status of all features.
