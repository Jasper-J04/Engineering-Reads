import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from xml.etree import ElementTree

from engineering_reads.contract import canonical_url


ROOT = Path(__file__).resolve().parents[1]
GUIDE = "queue-deduplication"
DIGEST = "safe-database-migrations"
GUIDE_URL = "https://example.org/engineering/queue-deduplication"


class SiteTest(unittest.TestCase):
    def setUp(self):
        work = tempfile.TemporaryDirectory()
        self.addCleanup(work.cleanup)
        self.repo = Path(work.name) / "site"
        shutil.copytree(
            ROOT,
            self.repo,
            ignore=shutil.ignore_patterns(
                ".git", ".venv", "__pycache__", "cache", "output", "output-demo",
            ),
        )
        self.demo = self.repo / "demo"

    def cli(self, *arguments, **settings):
        managed = {"CF_PAGES_BRANCH", "CF_PAGES_URL", "SITE_URL"}
        env = {key: value for key, value in os.environ.items() if key not in managed}
        return subprocess.run(
            [sys.executable, "-m", "engineering_reads", *arguments],
            cwd=self.repo,
            env={**env, **settings},
            capture_output=True,
            text=True,
            check=False,
        )

    def build(self, *arguments, **settings):
        result = self.cli("build", *arguments, **settings)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def guide_path(self):
        return self.demo / f"content/posts/{GUIDE}.md"

    def edit_guide(self, old, new):
        path = self.guide_path()
        path.write_text(path.read_text(encoding="utf-8").replace(old, new, 1), encoding="utf-8")

    def edit_state(self, edit):
        path = self.demo / "state/articles.json"
        state = json.loads(path.read_text(encoding="utf-8"))
        edit(state["articles"])
        path.write_text(json.dumps(state), encoding="utf-8")

    def test_demo_and_production_are_isolated(self):
        self.build("--demo", SITE_URL="https://reads.example")
        self.build()
        demo = self.repo / "output-demo"
        prod = self.repo / "output"
        home = (demo / "index.html").read_text(encoding="utf-8")
        self.assertLess(home.index(f"/posts/{GUIDE}/"), home.index(f"/posts/{DIGEST}/"))
        self.assertIn("示例", home)
        self.assertNotIn("/posts/", (prod / "index.html").read_text(encoding="utf-8"))
        self.assertFalse((prod / f"posts/{GUIDE}/index.html").exists())
        self.assertFalse(ElementTree.parse(prod / "rss.xml").findall("./channel/item"))

        guide = (demo / f"posts/{GUIDE}/index.html").read_text(encoding="utf-8")
        self.assertIn(GUIDE_URL, guide)
        self.assertIn("2026-11-21", guide)
        self.assertIn("<table>", guide)
        self.assertIn("<pre>", guide)
        digest = (demo / f"posts/{DIGEST}/index.html").read_text(encoding="utf-8")
        self.assertNotIn("Demo Editorial Team", digest)
        common_tag = (demo / "tags/engineering/index.html").read_text(encoding="utf-8")
        self.assertIn(f"/posts/{GUIDE}/", common_tag)
        self.assertIn(f"/posts/{DIGEST}/", common_tag)
        for path in ("tags/index.html", "archives/index.html", "about/index.html", "404.html"):
            self.assertTrue((demo / path).is_file(), path)
            self.assertTrue((prod / path).is_file(), path)

        feed = ElementTree.parse(demo / "rss.xml")
        self.assertEqual(
            [item.findtext("link") for item in feed.findall("./channel/item")],
            [f"https://reads.example/posts/{slug}/" for slug in (GUIDE, DIGEST)],
        )
        self.assertIn("梳理幂等键", feed.findtext("./channel/item/description"))
        self.assertNotIn("用业务操作确定幂等键", feed.findtext("./channel/item/description"))

    def test_pagination_uses_working_directory_links(self):
        original = self.guide_path().read_text(encoding="utf-8")
        for i in range(11):
            slug = f"another-guide-{i}"
            url = f"https://example.org/engineering/{slug}"
            draft = original.replace(GUIDE_URL, url).replace(f"Slug: {GUIDE}", f"Slug: {slug}")
            draft = draft.replace("2026-11-24T09:30:00", f"2026-11-20T09:{i:02}:00")
            (self.demo / f"content/posts/{slug}.md").write_text(draft, encoding="utf-8")
            self.edit_state(lambda articles: articles.update({
                url: {"source": "example-engineering", "status": "published", "attempts": 1, "slug": slug},
            }))
        self.build("--demo")
        out = self.repo / "output-demo"
        for prefix in ("", "tags/engineering/"):
            first = (out / prefix / "index.html").read_text(encoding="utf-8")
            self.assertIn(f'href="/{prefix}page/2/"', first)
            second = (out / prefix / "page/2/index.html").read_text(encoding="utf-8")
            self.assertIn("another-guide-0", second)
            self.assertIn(f'href="/{prefix}"', second)

    def test_urls_are_canonicalized_without_losing_meaningful_parameters(self):
        self.assertEqual(
            canonical_url("https://EXAMPLE.org:443/a/?id=1&utm_source=feed&id=2&fbclid=123#text"),
            "https://example.org/a?id=1&id=2",
        )

    def test_duplicate_source_url_blocks_the_build(self):
        post = self.guide_path().read_text(encoding="utf-8")
        (self.demo / "content/posts/duplicate.md").write_text(
            post.replace(f"Slug: {GUIDE}", "Slug: duplicate"), encoding="utf-8",
        )
        result = self.cli("build", "--demo")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate source URL", result.stderr)
        self.assertFalse((self.repo / "output-demo").exists())

    def test_published_records_must_match_posts(self):
        self.edit_state(lambda articles: articles.pop(GUIDE_URL))
        result = self.cli("validate", "--demo")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("every Markdown file needs a published record", result.stderr)

    def test_unknown_topic_blocks_the_build(self):
        self.edit_guide("Tags: engineering, distributed-systems", "Tags: invented")
        result = self.cli("build", "--demo")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("topic IDs", result.stderr)

    def test_full_translation_requires_approved_source(self):
        self.edit_guide("Kind: guide", "Kind: translation")
        result = self.cli("validate", "--demo")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("full translation requires an enabled source", result.stderr)

    def test_failed_article_can_be_retried_then_published(self):
        new_url = "https://example.org/engineering/pending"
        entry = {
            "source": "example-engineering", "status": "retry", "attempts": 1,
            "retry_at": "2026-11-25T09:30:00+08:00", "reason": "正文暂时无法读取",
        }
        self.edit_state(lambda articles: articles.update({new_url: entry}))
        self.build("--demo")
        new_post = self.demo / "content/posts/pending.md"
        self.assertFalse((self.repo / "output-demo/posts/pending/index.html").exists())
        new_post.write_text(
            self.guide_path().read_text(encoding="utf-8").replace(GUIDE_URL, new_url)
            .replace(f"Slug: {GUIDE}", "Slug: pending"),
            encoding="utf-8",
        )
        self.edit_state(lambda articles: articles.update({
            new_url: {"source": "example-engineering", "status": "published", "attempts": 2, "slug": "pending"},
        }))
        self.build("--demo")
        self.assertTrue((self.repo / "output-demo/posts/pending/index.html").is_file())
        result = self.cli("validate", "--demo")
        self.assertIn("Validated 3 articles.", result.stdout)

    def test_rendered_markdown_and_rss_are_sanitized(self):
        injected = '<script>alert(1)</script> [点击](javascript:alert(1))'
        self.edit_guide("Summary: ", f"Summary: {injected} ")
        with self.guide_path().open("a", encoding="utf-8") as post:
            post.write(f"\n{injected}\n\n<img src=\"https://example.org/track\">\n")
        self.build("--demo")
        output = self.repo / "output-demo"
        article = (output / f"posts/{GUIDE}/index.html").read_text(encoding="utf-8")
        summary = ElementTree.parse(output / "rss.xml").findtext("./channel/item/description")
        for value in (article, summary):
            self.assertNotIn("<script>alert(1)", value)
            self.assertNotIn("javascript:", value)
            self.assertNotIn("https://example.org/track", value)

    def test_cloudflare_production_requires_an_origin_and_rejects_demo(self):
        result = self.cli("build", CF_PAGES_BRANCH="main")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("SITE_URL", result.stderr)
        result = self.cli("build", "--demo", CF_PAGES_BRANCH="main", SITE_URL="https://reads.example")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("production content set", result.stderr)
        self.build(CF_PAGES_BRANCH="main", SITE_URL="https://reads.example")
        feed = ElementTree.parse(self.repo / "output/rss.xml")
        self.assertEqual(feed.findtext("./channel/link").rstrip("/"), "https://reads.example")


if __name__ == "__main__":
    unittest.main()
