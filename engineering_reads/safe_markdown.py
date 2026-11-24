"""Sanitize Markdown output before it reaches pages or feeds."""

from urllib.parse import urlsplit

import nh3
from markdown.extensions import Extension
from markdown.postprocessors import Postprocessor


def filter_attribute(tag, attribute, value):
    if tag == "img" and attribute == "src":
        try:
            url = urlsplit(value)
        except ValueError:
            return None
        local_figure = (
            not url.scheme and not url.netloc
            and url.path.startswith("/images/articles/")
            and url.path.endswith((".png", ".jpg"))
            and ".." not in url.path.split("/")
        )
        official_figure = url.scheme == "https" and (
            url.netloc == "assets.claude.com"
            or (url.netloc == "images.ctfassets.net" and url.path.startswith("/kftzwdyauwt9/"))
            or (url.netloc == "www.zhipuai.cn" and url.path.startswith("/api/media/file/"))
        )
        if not (local_figure or official_figure):
            return None
    return value


class SanitizeHtml(Postprocessor):
    def run(self, text):
        return nh3.clean(
            text,
            tags=nh3.ALLOWED_TAGS,
            attributes={**nh3.ALLOWED_ATTRIBUTES, "code": {"class"}},
            attribute_filter=filter_attribute,
            set_tag_attribute_values={
                "img": {"loading": "lazy", "decoding": "async", "referrerpolicy": "no-referrer"},
            },
            url_schemes={"https", "http"},
        )


class SafeMarkdown(Extension):
    def extendMarkdown(self, md):
        md.postprocessors.register(SanitizeHtml(md), "sanitize_html", 0)


def makeExtension(**kwargs):
    return SafeMarkdown(**kwargs)
