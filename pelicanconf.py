"""Pelican settings shared by local previews and Cloudflare Pages."""

import os
from pathlib import Path

from engineering_reads.contract import load_sources, read_json

AUTHOR = "Engineering Reads"
SITENAME = "Engineering Reads"
SITEDESCRIPTION = "国内外工程博客的中文导读与技术要点"
SITESUBTITLE = SITEDESCRIPTION
SITEURL = (
    os.getenv("SITE_URL")
    if os.getenv("CF_PAGES_BRANCH") in (None, "main")
    else os.getenv("CF_PAGES_URL")
) or "http://localhost:8000"
SITEURL = SITEURL.rstrip("/")
PREVIEW = os.getenv("CF_PAGES_BRANCH") not in (None, "main")
DEMO = os.getenv("ENGINEERING_READS_DEMO") == "1"
data_root = Path("demo") if DEMO else Path(".")
TIMEZONE = "Asia/Shanghai"
DEFAULT_LANG = "zh-cn"
DEFAULT_DATE_FORMAT = "%Y-%m-%d"

PATH = str(data_root / "content")
ARTICLE_PATHS = ["posts"]
PAGE_PATHS = []
STATIC_PATHS = ["images"]
THEME = "theme"
THEME_STATIC_DIR = "assets"
OUTPUT_PATH = "output-demo" if DEMO else "output"
JINJA_ENVIRONMENT = {"autoescape": True, "trim_blocks": True, "lstrip_blocks": True}
PLUGINS = []

ARTICLE_URL = "posts/{slug}/"
ARTICLE_SAVE_AS = "posts/{slug}/index.html"
ARTICLE_ORDER_BY = "reversed-date"
TAG_URL = "tags/{slug}/"
TAG_SAVE_AS = "tags/{slug}/index.html"
SLUGIFY_USE_UNICODE = True
DEFAULT_PAGINATION = 12
PAGINATED_TEMPLATES = {"index": None, "tag": None}
PAGINATION_PATTERNS = [
    (1, "{url}", "{save_as}"),
    (2, "{base_name}/page/{number}/", "{base_name}/page/{number}/index.html"),
]
INDEX_SAVE_AS = "index.html"
INDEX_URL = ""
TAGS_SAVE_AS = "tags/index.html"
TAGS_URL = "tags/"
ARCHIVES_SAVE_AS = "archives/index.html"
ARCHIVES_URL = "archives/"
ABOUT_SAVE_AS = "about/index.html"
ABOUT_URL = "about/"
DIRECT_TEMPLATES = ["index", "tags", "archives", "search_index", "about", "404"]
SEARCH_INDEX_SAVE_AS = "search-index.json"
CATEGORY_SAVE_AS = ""
AUTHOR_SAVE_AS = ""

FEED_ALL_RSS = "rss.xml"
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None
FEED_MAX_ITEMS = 30
RSS_FEED_SUMMARY_ONLY = True
FORMATTED_FIELDS = ["summary"]
MARKDOWN = {
    "extensions": ["fenced_code", "tables", "engineering_reads.safe_markdown"],
    "output_format": "html",
}
SOURCES = load_sources(data_root)
TOPICS = read_json(Path("topics.json"))
