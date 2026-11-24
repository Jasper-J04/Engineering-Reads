"""Validate the repository contract used by the scheduled GPT task."""

import json
import re
from datetime import date, datetime
from pathlib import Path
from urllib.parse import unquote_plus, urlsplit, urlunsplit


SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
DATE_TIME = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+08:00")
REQUIRED = {"Title", "Slug", "Date", "Summary", "Tags", "Source", "Source_url", "Source_title", "Kind"}
OPTIONAL = {"Source_author", "Source_date", "Source_license", "Source_license_url"}


class ContractError(ValueError):
    pass


def require(condition, context, message):
    if not condition:
        raise ContractError(f"{context}: {message}")


def text(value):
    return (
        isinstance(value, str)
        and bool(value)
        and value == value.strip()
        and value.isprintable()
    )


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, key, "duplicate JSON key")
        result[key] = value
    return result


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    except (OSError, ValueError) as error:
        raise ContractError(f"{path.name}: {error}") from error


def canonical_url(value):
    if not text(value) or any(char.isspace() for char in value) or "\\" in value:
        raise ContractError("expected an HTTPS URL without whitespace")
    try:
        parts = urlsplit(value)
        host = parts.hostname
        port = parts.port
    except ValueError as error:
        raise ContractError(f"invalid URL: {value}") from error
    require(
        parts.scheme == "https" and host and port in (None, 443)
        and parts.username is None and parts.password is None and ":" not in host,
        value,
        "expected a public HTTPS URL",
    )
    query = []
    for item in parts.query.split("&"):
        key = unquote_plus(item.partition("=")[0]).lower()
        if not key.startswith("utm_") and key not in {"gclid", "fbclid"}:
            query.append(item)
    return urlunsplit(("https", host, parts.path.rstrip("/") or "/", "&".join(query), ""))


def timestamp(value, context):
    require(isinstance(value, str) and DATE_TIME.fullmatch(value), context,
            "use YYYY-MM-DDTHH:MM:SS+08:00")
    try:
        return datetime.fromisoformat(value)
    except ValueError as error:
        raise ContractError(f"{context}: invalid timestamp") from error


def load_sources(root):
    config = read_json(root / "sources.json")
    require(isinstance(config, dict) and isinstance(config.get("sources"), list),
            "sources.json", "expected a sources list")
    sources = {}
    keys = {"id", "name", "language", "feed", "hosts", "allow_full_translation"}
    for source in config["sources"]:
        require(isinstance(source, dict) and source.keys() == keys,
                "sources.json", "invalid source fields")
        sid = source["id"]
        require(text(sid) and SLUG.fullmatch(sid) and sid not in sources,
                "sources.json", "invalid or duplicate source id")
        require(text(source["name"]) and source["language"] in ("zh", "en"),
                sid, "expected a name and language zh or en")
        hosts = source["hosts"]
        require(isinstance(hosts, list) and hosts and all(
            text(host) and re.fullmatch(r"[a-z0-9.-]+", host) for host in hosts
        ), sid, "expected a list of lowercase hostnames")
        canonical_url(source["feed"])
        require(type(source["allow_full_translation"]) is bool,
                sid, "expected a boolean translation policy")
        sources[sid] = source
    return sources


def check_source(source_id, url, sources, context):
    require(isinstance(source_id, str) and source_id in sources, context, "unknown source")
    require(canonical_url(url) == url, context, "source URL must be canonical")
    source = sources[source_id]
    require(urlsplit(url).hostname in source["hosts"], context, "source host is not approved")
    return source


def validate_post(path, sources, topics):
    context = path.name
    require(path.is_file() and not path.is_symlink() and path.stat().st_size <= 128 * 1024,
            context, "expected a Markdown file of at most 128 KiB")
    raw = path.read_text(encoding="utf-8")
    header, separator, body = raw.partition("\n\n")
    require(separator and body.strip(), context, "expected metadata, blank line, and body")
    fields = {}
    for line in header.splitlines():
        key, colon, value = line.partition(": ")
        require(colon and key in REQUIRED | OPTIONAL and key not in fields and text(value),
                context, f"invalid metadata line for {key!r}")
        fields[key] = value
    require(REQUIRED <= fields.keys(), context, f"missing fields: {', '.join(sorted(REQUIRED - fields.keys()))}")
    slug = fields["Slug"]
    require(len(slug) <= 80 and SLUG.fullmatch(slug) and slug == path.stem,
            context, "slug must match the filename and use lowercase ASCII words")
    timestamp(fields["Date"], f"{context} Date")
    tags = fields["Tags"].split(", ")
    require(1 <= len(tags) <= 5 and len(tags) == len(set(tags)) and all(tag in topics for tag in tags),
            context, "use 1–5 distinct topic IDs separated by comma and space")
    source = check_source(fields["Source"], fields["Source_url"], sources, context)
    kind = fields["Kind"]
    expected_kind = "digest" if source["language"] == "zh" else "guide"
    if kind == "translation":
        require(source["language"] == "en" and source["allow_full_translation"]
                and "Source_license" in fields and "Source_license_url" in fields,
                context, "full translation requires an enabled source and documented permission")
    else:
        require(kind == expected_kind, context, f"expected {expected_kind}")
    if "Source_date" in fields:
        try:
            source_date = date.fromisoformat(fields["Source_date"])
        except ValueError as error:
            raise ContractError(f"{context}: invalid Source_date") from error
        require(source_date.isoformat() == fields["Source_date"], context, "use YYYY-MM-DD")
    if "Source_license_url" in fields:
        canonical_url(fields["Source_license_url"])
        require("Source_license" in fields, context, "license URL needs a license name")
    return fields


def validate_state(root, sources, posts):
    state = read_json(root / "state/articles.json")
    require(isinstance(state, dict) and state.keys() == {"version", "articles"}
            and type(state["version"]) is int and state["version"] == 1
            and isinstance(state["articles"], dict),
            "state/articles.json", "expected state schema version 1")
    published = set()
    common = {"source", "status", "attempts"}
    extra = {"pending": set(), "retry": {"retry_at", "reason"},
             "held": {"reason"}, "published": {"slug"}}
    for url, entry in state["articles"].items():
        require(isinstance(entry, dict) and common <= entry.keys(), url, "invalid state record")
        check_source(entry["source"], url, sources, url)
        status = entry["status"]
        require(isinstance(status, str) and status in extra and entry.keys() == common | extra[status],
                url, "invalid status or state fields")
        attempts = entry["attempts"]
        require(type(attempts) is int and ((attempts == 0) if status == "pending" else 1 <= attempts <= 3),
                url, "invalid attempts count")
        if status == "retry":
            require(attempts < 3, url, "move exhausted retries to held")
            timestamp(entry["retry_at"], f"{url} retry_at")
        if status in {"retry", "held"}:
            require(text(entry["reason"]) and len(entry["reason"]) <= 240,
                    url, "expected a short failure reason")
        if status == "published":
            post = posts.get(url)
            require(post and entry["slug"] == post["Slug"] and entry["source"] == post["Source"],
                    url, "published record must match a Markdown file")
            published.add(url)
    require(published == posts.keys(), "state/articles.json", "every Markdown file needs a published record")


def validate(root: Path, topics_path: Path | None = None):
    sources = load_sources(root)
    topics = read_json(topics_path or root / "topics.json")
    require(isinstance(topics, dict) and bool(topics) and all(
        SLUG.fullmatch(key) and text(label) for key, label in topics.items()
    ), "topics.json", "expected a mapping of topic IDs to labels")
    posts = {}
    for path in sorted((root / "content/posts").iterdir()):
        if path.name == ".gitkeep":
            continue
        require(path.suffix == ".md", path.name, "only flat .md files are supported")
        post = validate_post(path, sources, topics)
        url = post["Source_url"]
        require(url not in posts, path.name, f"duplicate source URL {url}")
        posts[url] = post
    validate_state(root, sources, posts)
    return len(posts)
