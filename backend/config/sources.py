"""Registry of all news sources with trust scores and feed URLs."""

SOURCES = {
    "hacker_news": {
        "name": "Hacker News",
        "type": "api",
        "trust_score": 0.9,
        "base_url": "https://hacker-news.firebaseio.com/v0",
    },
    "hn_algolia": {
        "name": "Hacker News (Search)",
        "type": "api",
        "trust_score": 0.9,
        "base_url": "https://hn.algolia.com/api/v1",
    },
    "newsapi": {
        "name": "NewsAPI",
        "type": "key_api",
        "trust_score": 0.7,
        "base_url": "https://newsapi.org/v2",
    },
    "dev_community": {
        "name": "DEV Community",
        "type": "rss",
        "trust_score": 0.75,
        "feed_url": "https://dev.to/feed",
    },
    "freecodecamp": {
        "name": "freeCodeCamp",
        "type": "rss",
        "trust_score": 0.8,
        "feed_url": "https://www.freecodecamp.org/news/rss/",
    },
    "google_developers": {
        "name": "Google Developers Blog",
        "type": "rss",
        "trust_score": 0.85,
        "feed_url": "https://developers.googleblog.com/feeds/posts/default?alt=rss",
    },
    "dzone": {
        "name": "DZone",
        "type": "rss",
        "trust_score": 0.7,
        "feed_url": "https://feeds.dzone.com/home",
    },
    "wired": {
        "name": "Wired",
        "type": "rss",
        "trust_score": 0.75,
        "feed_url": "https://www.wired.com/feed/rss",
    },
    "android_authority": {
        "name": "Android Authority",
        "type": "rss",
        "trust_score": 0.75,
        "feed_url": "https://www.androidauthority.com/feed/",
    },
    "techcrunch": {
        "name": "TechCrunch",
        "type": "rss",
        "trust_score": 0.8,
        "feed_url": "https://techcrunch.com/feed/",
    },
    "infoq": {
        "name": "InfoQ",
        "type": "rss",
        "trust_score": 0.85,
        "feed_url": "https://feed.infoq.com/",
    },
    "github_blog": {
        "name": "GitHub Blog",
        "type": "rss",
        "trust_score": 0.85,
        "feed_url": "https://github.blog/feed/",
    },
}

PAGE_SIZE = 10
