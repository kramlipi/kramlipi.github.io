"""MkDocs hooks — keep GitHub Pages SEO files correct after build."""

from __future__ import annotations

import gzip
import re
from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
SITEMAP_NS = NS["sm"]
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
    ET.register_namespace("", SITEMAP_NS)
    site_dir = Path(config["site_dir"])
    site_url = (config.get("site_url") or "").rstrip("/")
    if not site_url:
        raise RuntimeError("site_url must be set in mkdocs.yml for sitemap generation")

    (site_dir / ".nojekyll").touch()
    sitemap = site_dir / "sitemap.xml"
    robots = site_dir / "robots.txt"
    if not sitemap.is_file():
        raise RuntimeError(f"missing sitemap after build: {sitemap}")
    if not robots.is_file():
        raise RuntimeError(f"missing robots.txt after build: {robots}")

    noindex_urls = _noindex_urls(site_dir, site_url)
    urls = _read_sitemap_urls(sitemap, site_url)
    urls = [url for url in urls if url not in noindex_urls]
    _write_sitemap(sitemap, urls)
    _write_sitemap_gz(site_dir / "sitemap.xml.gz", sitemap)


def _canonical_url(site_dir: Path, html: Path, site_url: str) -> str:
    rel = html.relative_to(site_dir).as_posix()
    if rel.endswith("/index.html"):
        rel = rel[: -len("index.html")]
    elif rel == "index.html":
        rel = ""
    return f"{site_url}/{rel}"


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


def _read_sitemap_urls(sitemap: Path, site_url: str) -> list[str]:
    tree = ET.parse(sitemap)
    root = tree.getroot()
    urls: list[str] = []
    for url_el in root.findall("sm:url", NS):
        loc = url_el.find("sm:loc", NS)
        if loc is None or not loc.text:
            continue
        loc_text = loc.text.strip()
        if not loc_text.startswith(f"{site_url}/") and loc_text != f"{site_url}/":
            raise RuntimeError(f"sitemap URL outside site_url ({site_url}): {loc_text}")
        urls.append(loc_text)
    if not urls:
        raise RuntimeError(f"sitemap is empty: {sitemap}")
    return urls


def _write_sitemap(sitemap: Path, urls: list[str]) -> None:
    root = ET.Element(f"{{{SITEMAP_NS}}}urlset")
    today = date.today().isoformat()
    for loc in urls:
        url_el = ET.SubElement(root, f"{{{SITEMAP_NS}}}url")
        loc_el = ET.SubElement(url_el, f"{{{SITEMAP_NS}}}loc")
        loc_el.text = loc
        lastmod_el = ET.SubElement(url_el, f"{{{SITEMAP_NS}}}lastmod")
        lastmod_el.text = today
    tree = ET.ElementTree(root)
    tree.write(sitemap, encoding="utf-8", xml_declaration=True)


def _write_sitemap_gz(gz_path: Path, sitemap: Path) -> None:
    with sitemap.open("rb") as src, gzip.open(gz_path, "wb", compresslevel=9) as dst:
        dst.write(src.read())
