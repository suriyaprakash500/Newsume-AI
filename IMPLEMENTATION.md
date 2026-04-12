# Newsume AI — Implementation Plan & Status

## Product Goal

**Newsume AI** — An AI that reads your resume and delivers personalized news.

Build a habit-forming career-action app that helps users make career decisions daily in under 2 minutes, powered by resume-based personalization and 12 free/freemium news sources.

---

## Phase 1 — Core Loop (DONE)

### Career Impact Card
- **Backend**: `backend/services/career_impact_service.py`
  - `generate_career_impacts_batch()` — batches up to 5 articles in one Gemini call for cost efficiency
  - Per-article cache by title hash to avoid re-generation
  - Fallback keyword-based impact when no API key
- **Android**: `NewsScreen.kt` — expandable career impact card below each article with icon and "Next step" label
- **API**: enrichment runs automatically during `POST /news/{device_id}/refresh`

### Daily 2-Minute Digest
- **Backend**: `backend/services/career_impact_service.py`
  - `generate_daily_digest()` — 5 bullet summary + 1 recommended action from top articles
  - Fallback: article titles as bullets when Gemini unavailable
- **Android**: `DigestScreen.kt` — dedicated tab with headline cards and action recommendation
- **API**: `GET /news/{device_id}/digest`

### User-Editable Profile
- **Backend**: `backend/api/routes_resume.py`
  - `PUT /resume/profile/{device_id}` — accepts edited skills, certifications, keywords, experience, education
  - Increments profile version on each edit
- **Android**: `ProfileScreen.kt` — edit icon per section, add/remove chips, Save button persists to backend

---

## Phase 2 — Reliable Free Data Stack (DONE)

### Multi-Source Aggregator
- **Orchestrator**: `backend/services/source_aggregator.py`
  - Fetches from all sources in priority order
  - URL hash + title hash deduplication
  - Source trust score stamping from config
  - Graceful fallback when any source fails

### Sources Implemented

| Source | File | Type | Auth | Trust |
|--------|------|------|------|-------|
| Hacker News (Top) | `services/hn_fetcher.py` | Firebase API | No key | 0.9 |
| Hacker News (Search) | `services/hn_fetcher.py` | Algolia API | No key | 0.9 |
| DEV Community | `services/rss_fetcher.py` | RSS | No key | 0.75 |
| freeCodeCamp | `services/rss_fetcher.py` | RSS | No key | 0.8 |
| Google Developers Blog | `services/rss_fetcher.py` | RSS | No key | 0.85 |
| DZone | `services/rss_fetcher.py` | RSS | No key | 0.7 |
| Wired | `services/rss_fetcher.py` | RSS | No key | 0.75 |
| Android Authority | `services/rss_fetcher.py` | RSS | No key | 0.75 |
| TechCrunch | `services/rss_fetcher.py` | RSS | No key | 0.8 |
| InfoQ | `services/rss_fetcher.py` | RSS | No key | 0.85 |
| GitHub Blog | `services/rss_fetcher.py` | RSS | No key | 0.85 |
| NewsAPI | `services/news_fetcher.py` | Key API | API key | 0.7 |

(9 RSS + 2 Hacker News APIs + 1 key-based API = 12 total; 11 are completely free)

### Source Config
- **Registry**: `backend/config/sources.py` — all sources with name, type, trust score, feed URL
- **Content policy**: metadata only (title, snippet, source, URL). No full-body republishing.

### Pagination & Unread Feed
- **Backend**: `backend/repositories/news_repo.py`
  - `get_unread_articles()` — offset-based pagination, sorted by relevance score, excludes read article IDs
  - `mark_articles_read()` — persists read state in `article_read_states` table
  - `get_unread_count()` — total unread for device
  - `delete_old_articles()` — retention cleanup (keeps latest 200)
- **API**: `GET /news/{device_id}?limit=10&offset=0` — unread only, 10 per page
- **API**: `POST /news/{device_id}/mark-read` — mark article IDs as seen
- **Android**: `NewsScreen.kt` auto-marks visible articles as read; "You're all caught up!" state when empty

---

## Phase 3 — India Relevance Layer (DONE)

### India Context Service
- **File**: `backend/utils/india_context.py` (pure utils, no service dependencies)
- **Sectors covered**: fintech/UPI, ONDC/public infra, Indian startups, GCC hiring
- **Cities**: Bengaluru, Hyderabad, Pune, Chennai, NCR, Mumbai, Kolkata
- **General terms**: India, NASSCOM, Infosys, TCS, Wipro, HCL, etc.
- `compute_india_boost()` — returns 0.0-0.3 boost + matched terms
- `get_city_demand_label()` — returns city name if mentioned

### Integrated Into Scoring
- **File**: `backend/utils/relevance_scorer.py`
- Formula: `(skill_match * 0.6) + (source_trust * 0.25) + (india_boost * 0.15)`
- India terms appear in matched_skills for transparency

---

## Phase 4 — Retention & Trust (DONE)

### Bookmarks + Notes
- **Backend model**: `backend/models/bookmark.py`
- **Backend repo**: `backend/repositories/bookmark_repo.py`
- **Backend API**: `backend/api/routes_bookmarks.py`
  - `POST /bookmarks/{device_id}` — add with optional note
  - `DELETE /bookmarks/{device_id}/{article_id}` — remove
  - `GET /bookmarks/{device_id}` — list all with article metadata
- **Android**: bookmark icon on each article card in `NewsScreen.kt`; Room tracks `isBookmarked` + `bookmarkNote`

### Relevance Scoring
- **Trust-weighted**: source trust score affects ranking (0.25 weight)
- **India-boosted**: India context adds up to 0.15 weight
- **Skill-matched**: profile skill/keyword match is 0.6 weight

---

## Phase 5 — Personalization & Intelligence (DONE)

### Personalization Controls
- **Backend**: `backend/services/personalization_service.py`
  - `apply_topic_filter()` — boost preferred topics, filter out blocked topics
  - `apply_seniority_filter()` — boost beginner/advanced content based on user level
  - 18 valid topics (AI, ML, frontend, backend, cloud, devops, mobile, etc.)
  - 5 seniority levels (student, junior, mid, senior, lead)
- **API**: `GET /preferences/topics` — list all available topics and seniority levels
- **API**: `GET /preferences/{device_id}` — get current user preferences
- **API**: `PUT /preferences/{device_id}` — set preferred/blocked topics, seniority, notification settings, quiet hours
- Applied in both manual refresh and scheduled daily job

### Skill-Gap Report
- **Backend**: `backend/services/skill_gap_service.py`
  - Gemini compares user skills against trending article topics
  - Returns: trending skills, missing skills, recommendation, resume suggestions
  - Fallback keyword-based analysis when Gemini unavailable
- **API**: `GET /preferences/{device_id}/skill-gap`

### Retention Metrics
- **Backend model**: `backend/models/metrics.py` — `user_metrics` table
- **Backend repo**: `backend/repositories/metrics_repo.py`
  - Event logging (digest_open, article_click, refresh, bookmark, app_open)
  - 7-day activity stats and active day calculation
- **API**: `POST /preferences/{device_id}/track` — log user events
- **API**: `GET /preferences/{device_id}/metrics` — 7-day retention stats

### Notification Guardrails
- **Backend**: `backend/services/notification_service.py`
  - Quiet hours (configurable, default 10 PM–7 AM)
  - Once-per-day dedup per device
  - `notify_enabled` toggle per user
- **Android**: `NewsSyncWorker.kt` — SDK version-aware permission check (API 33+ guard)

---

## Phase 6 — LLM Reliability (DONE)

### Gemini Client
- **File**: `backend/utils/gemini_client.py`
  - Lazy singleton model initialization (configures once)
  - `generate_json()` — async, runs in thread pool to avoid blocking the event loop
  - Retry with exponential backoff on 429/5xx errors (2 retries)
  - `validate_keys()` — ensures LLM JSON output has required keys with correct types, fills defaults for missing fields
  - Handles non-dict responses (arrays, nulls) gracefully

### Resume Processing
- Input truncation to 8000 chars (preserves last complete line)
- Improved fallback extraction: regex email, experience keyword parsing
- **File**: `backend/services/skill_extractor.py`

---

## Phase 7 — Code Quality & Audit Fixes (DONE)

Two full-codebase audits identified and resolved 35+ issues across backend and Android.

### Backend Fixes
- **Layer violation fixed**: `utils/relevance_scorer.py` was importing from `services/` — moved India boost logic to `utils/india_context.py` (pure utils, zero service dependencies)
- **Async event loop safety**: `generate_json()` was blocking the FastAPI event loop with `time.sleep` during retries — now runs sync Gemini calls in a thread pool via `asyncio.to_thread()`
- **Pagination correctness**: Cursor-based `id < after_id` was incompatible with relevance-sorted results — switched to offset-based pagination
- **File upload safety**: Removed `.doc` from allowed file types (python-docx only supports `.docx`, not legacy binary `.doc`)
- **Personalization gap**: Manual refresh (`POST /news/{device_id}/refresh`) was ignoring user topic/seniority preferences — now loads and applies them like the scheduled job
- **LLM output safety**: `validate_keys()` crashed on non-dict Gemini responses — added type guard; fixed fragile `_model._model_name` private attribute access
- **DRY**: Extracted `_serialize_profile()` helper to eliminate 3x duplicated JSON serialization
- **Cleanup**: Removed unused `feedparser` dependency, unused imports (`lru_cache`, `json`), consolidated duplicate `PAGE_SIZE` constant
- **Model registration**: Added `import models` in `main.py` lifespan to ensure all ORM models are registered before `create_all()`
- **Package consistency**: Added `__init__.py` to all 5 packages missing them
- **API layer purity**: Moved direct `db.query()` from `routes_bookmarks.py` into `news_repo.get_article_by_id()`

### Android Fixes
- **Compile fix**: Updated Compose BOM from `2024.04.01` to `2024.10.00` (`PullToRefreshBox` was unavailable in old BOM)
- **Profile save wired up**: Edit UI was dead (no save button, no API call) — added `editProfile()` to Repository, `saveProfileEdits()` to ViewModel, Save button + snackbar feedback in ProfileScreen
- **NPE prevention**: Added defaults to all `ProfileDto` fields to handle partial backend responses via Gson
- **Notification fix**: `POST_NOTIFICATIONS` permission check fails on API 26-32 — added `Build.VERSION >= TIRAMISU` guard
- **SnackbarHost placement**: Moved from inside scrollable `Column` to proper `Scaffold` slot in ProfileScreen
- **State management**: `uploadResume()` was resetting entire UI state — changed to `copy()` to preserve existing fields
- **File picker safety**: Restricted MIME types from `application/*` to PDF + DOCX only via `OpenDocument` contract
- **Flag cleanup**: `uploadSuccess` was never cleared — added `clearUploadSuccess()` after snackbar
- **Caught-up state**: `syncFromServer()` now updates `isCaughtUp` so first load shows correct empty state
- **Shared ViewModel**: `NewsViewModel` hoisted to `AppNavigation` level — `DigestScreen` and `NewsScreen` share one instance
- **Explicit Gson**: Added `com.google.code.gson:gson:2.10.1` as explicit dependency

---

## Architecture

### Backend (Python FastAPI)

```
backend/
├── api/
│   ├── routes_resume.py         # Upload, profile GET/PUT, FCM token
│   ├── routes_news.py           # Unread feed, all feed, refresh, digest, mark-read
│   ├── routes_bookmarks.py      # Bookmark CRUD
│   └── routes_preferences.py    # Topic prefs, seniority, metrics, skill-gap
├── services/
│   ├── source_aggregator.py     # Multi-source fetch + dedup orchestrator
│   ├── hn_fetcher.py            # Hacker News Firebase + Algolia
│   ├── rss_fetcher.py           # RSS feed parser (9 sources)
│   ├── news_fetcher.py          # NewsAPI integration
│   ├── career_impact_service.py # Gemini career cards + digest (batched)
│   ├── personalization_service.py # Topic/seniority filtering
│   ├── skill_gap_service.py     # AI skill-gap analysis
│   ├── india_context_service.py # Re-exports from utils for backwards compat
│   ├── news_ranker.py           # Rank + enrich + personalize pipeline
│   ├── skill_extractor.py       # Gemini resume extraction
│   ├── resume_parser.py         # Upload orchestration
│   ├── scheduler_service.py     # Daily 9 AM cron job
│   └── notification_service.py  # Firebase push + quiet hours + dedup
├── repositories/
│   ├── user_profile_repo.py     # Profile CRUD
│   ├── news_repo.py             # Articles + read-state CRUD
│   ├── bookmark_repo.py         # Bookmark CRUD
│   └── metrics_repo.py          # Retention event logging + stats
├── models/
│   ├── user_profile.py          # UserProfile table (+ preference fields)
│   ├── news_article.py          # NewsArticle + ArticleReadState tables
│   ├── bookmark.py              # Bookmark table
│   └── metrics.py               # UserMetric table
├── utils/
│   ├── gemini_client.py         # Async Gemini singleton + retry + validation
│   ├── text_parser.py           # PDF/DOCX text extraction
│   ├── india_context.py         # India relevance boosting (pure utils)
│   └── relevance_scorer.py      # Scoring with trust + India boost
├── config/
│   ├── settings.py              # Env-driven config (Pydantic Settings)
│   └── sources.py               # Source registry + trust scores + PAGE_SIZE
├── database.py                  # SQLAlchemy engine + session
├── main.py                      # FastAPI app + scheduler + model registration
├── Dockerfile
└── docker-compose.yml
```

### Android (Kotlin + Jetpack Compose)

```
android/app/src/main/java/com/resumenews/app/
├── MainActivity.kt
├── ResumeNewsApp.kt             # Notification channel + WorkManager
├── data/
│   ├── local/
│   │   ├── AppDatabase.kt       # Room DB (v2)
│   │   ├── dao/
│   │   │   ├── UserProfileDao.kt
│   │   │   └── NewsArticleDao.kt  # Unread, bookmarked, mark-read queries
│   │   └── entity/
│   │       ├── UserProfileEntity.kt
│   │       └── NewsArticleEntity.kt  # + career fields, isRead, isBookmarked
│   ├── remote/
│   │   ├── ApiService.kt        # All endpoints including edit, digest, bookmarks, prefs
│   │   ├── RetrofitClient.kt
│   │   └── dto/
│   │       ├── ProfileResponse.kt  # ProfileDto, EditProfileBody
│   │       └── NewsResponse.kt     # ArticleDto, DigestDto, BookmarkDto, RefreshResponse
│   └── repository/
│       ├── ResumeRepository.kt   # Upload, fetch, editProfile
│       └── NewsRepository.kt     # Unread feed, bookmarks, digest, mark-read
├── viewmodel/
│   ├── ResumeViewModel.kt        # Upload + saveProfileEdits
│   └── NewsViewModel.kt          # Refresh, digest, bookmarks, mark-read, caught-up state
├── ui/
│   ├── navigation/AppNavigation.kt  # 4 tabs: Resume, News, Digest, Profile (shared ViewModel)
│   ├── screens/
│   │   ├── ResumeScreen.kt       # File picker (PDF/DOCX only), upload flow
│   │   ├── NewsScreen.kt         # Career impact cards, bookmark, pull-to-refresh, auto mark-read
│   │   ├── DigestScreen.kt       # Daily career briefing
│   │   └── ProfileScreen.kt      # Editable skills/keywords + Save button in Scaffold
│   └── theme/
│       ├── Color.kt
│       ├── Type.kt
│       └── Theme.kt
└── worker/
    └── NewsSyncWorker.kt          # Background sync + local notification (API 26+ safe)
```

---

## API Endpoints Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/resume/upload` | Upload resume (PDF/DOCX) |
| GET | `/resume/profile/{device_id}` | Get extracted profile |
| PUT | `/resume/profile/{device_id}` | Edit profile fields |
| POST | `/resume/fcm-token` | Register push token |
| GET | `/news/{device_id}` | Unread articles (10/page, offset) |
| GET | `/news/{device_id}/all` | All articles (offset pagination) |
| POST | `/news/{device_id}/refresh` | Fetch + rank + personalize from all sources |
| POST | `/news/{device_id}/mark-read` | Mark articles as seen |
| GET | `/news/{device_id}/digest` | Daily career digest |
| POST | `/bookmarks/{device_id}` | Add bookmark |
| DELETE | `/bookmarks/{device_id}/{id}` | Remove bookmark |
| GET | `/bookmarks/{device_id}` | List bookmarks |
| GET | `/preferences/topics` | List available topics & seniority levels |
| GET | `/preferences/{device_id}` | Get user preference settings |
| PUT | `/preferences/{device_id}` | Update topics, seniority, notifications, quiet hours |
| POST | `/preferences/{device_id}/track` | Log user events for retention metrics |
| GET | `/preferences/{device_id}/metrics` | 7-day retention stats |
| GET | `/preferences/{device_id}/skill-gap` | AI skill-gap report |
| GET | `/health` | Health check |

---

## Future Work (Not Yet Implemented)

- Interview discussion prompts from top stories
- Regional language summaries (Hindi/Tamil/Telugu)
- Streak/goals (non-gimmicky daily reads target)
- LinkedIn post draft export from bookmarks
- Credibility scoring per article (cross-source confirmation)
- Authentication (API key or JWT per device)
- Rate limiting on refresh endpoint
- Proper Room database migration (currently uses destructive migration)
