"""MkDocs hooks — keep GitHub Pages SEO files correct after build."""

from __future__ import annotations

import gzip
import re
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
NOINDEX_RE = re.compile(
    rb'<meta\s+name=["\']robots["\']\s+content=["\'][^"\']*noindex',
    re.IGNORECASE,
)


def on_post_build(config, **kwargs):
    """Ensure crawlers can fetch sitemap/robots and drop noindex URLs.

    GitHub Actions upload-pages-artifact only ships the site/ directory.
    Without .nojekyll, Pages may run Jekyll and Google Search Console
    reports "Couldn't fetch" for sitemap.xml (browsers can still get 200).
    """
    ET.register_namespace("", NS["sm"])
    site_dir = Path(config["site_dir"])
    (site_dir / ".nojekyll").touch()
    sitemap = site_dir / "sitemap.xml"
    robots = site_dir / "robots.txt"
    if not sitemap.is_file():
        raise RuntimeError(f"missing sitemap after build: {sitemap}")
    if not robots.is_file():
        raise RuntimeError(f"missing robots.txt after build: {robots}")

    noindex_urls = _noindex_urls(site_dir, config.get("site_url") or "")
    if noindex_urls:
        _strip_sitemap_urls(sitemap, noindex_urls)
        gz = site_dir / "sitemap.xml.gz"
        if gz.is_file():
            with sitemap.open("rb") as src, gzip.open(gz, "wb") as dst:
                dst.write(src.read())


def _canonical_url(site_dir: Path, html: Path, site_url: str) -> str:
    rel = html.relative_to(site_dir).as_posix()
    if rel.endswith("/index.html"):
        rel = rel[: -len("index.html")]
    elif rel == "index.html":
        rel = ""
    return f"{site_url.rstrip('/')}/{rel}"


def _noindex_urls(site_dir: Path, site_url: str) -> set[str]:
    found: set[str] = set()
    for html in site_dir.rglob("*.html"):
        try:
            head = html.read_bytes()[:16384]
        except OSError:
            continue
        if NOINDEX_RE.search(head):
            found.add(_canonical_url(site_dir, html, site_url))
    return found


def _strip_sitemap_urls(sitemap: Path, drop: set[str]) -> None:
    tree = ET.parse(sitemap)
    root = tree.getroot()
    removed = 0
    for url in list(root.findall("sm:url", NS)):
        loc = url.find("sm:loc", NS)
        if loc is None or loc.text is None:
            continue
        if loc.text.strip() in drop:
            root.remove(url)
            removed += 1
    if removed:
        tree.write(sitemap, encoding="utf-8", xml_declaration=True)
