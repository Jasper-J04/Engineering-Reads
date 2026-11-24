"""Sanitize Markdown output before it reaches pages or feeds."""

import nh3
from markdown.extensions import Extension
from markdown.postprocessors import Postprocessor


class SanitizeHtml(Postprocessor):
    def run(self, text):
        return nh3.clean(
            text,
            tags=nh3.ALLOWED_TAGS - {"img"},
            attributes={**nh3.ALLOWED_ATTRIBUTES, "code": {"class"}},
            url_schemes={"https", "http"},
        )


class SafeMarkdown(Extension):
    def extendMarkdown(self, md):
        md.postprocessors.register(SanitizeHtml(md), "sanitize_html", 0)


def makeExtension(**kwargs):
    return SafeMarkdown(**kwargs)
