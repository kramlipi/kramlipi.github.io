"""MkDocs hooks — keep GitHub Pages SEO files correct after build."""

from __future__ import annotations

import html
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
    _write_html_sitemap(site_dir, site_url, urls)
    _remove_gz_sitemap(site_dir)
    _write_article_md_redirects(site_dir, site_url)
    _write_legacy_feature_redirects(site_dir, site_url)




LEGACY_FEATURE_REDIRECTS: dict[str, str] = {
    "auto-verify": "features/auto-verify/",
    "flaky-test-admin": "features/flaky-test-admin/",
    "linter-sandbox": "features/linter-sandbox/",
    "ultra-intelligence": "features/ultra-intelligence/",
    "coverage": "features/coverage/",
    "articles/smarter-testing-m1-test-intel": "features/smarter-testing-m1-test-intel/",
}


def _redirect_html(target: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="refresh" content="0; url={html.escape(target, quote=True)}">
  <link rel="canonical" href="{html.escape(target, quote=True)}">
  <script>location.replace({target!r});</script>
  <title>Redirecting…</title>
</head>
<body>
  <p>Moved to <a href="{html.escape(target, quote=True)}">{html.escape(target)}</a>.</p>
</body>
</html>
"""


def _write_legacy_feature_redirects(site_dir: Path, site_url: str) -> None:
    """301-style HTML redirects for feature pages moved under /features/."""
    for old_path, new_rel in LEGACY_FEATURE_REDIRECTS.items():
        target = f"{site_url}/{new_rel}"
        dest = site_dir.joinpath(*old_path.split("/"))
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "index.html").write_text(
            _redirect_html(target), encoding="utf-8", newline="\n"
        )
        # Legacy *.md URL stubs (GitHub Pages / bookmarks)
        if "/" in old_path:
            stub_dir = site_dir / old_path.rsplit("/", 1)[0]
            stub_name = f"{old_path.rsplit('/', 1)[1]}.md"
        else:
            stub_dir = site_dir
            stub_name = f"{old_path}.md"
        stub_dir.mkdir(parents=True, exist_ok=True)
        (stub_dir / stub_name).write_text(
            _redirect_html(target), encoding="utf-8", newline="\n"
        )


def _write_article_md_redirects(site_dir: Path, site_url: str) -> None:
    """Redirect legacy *.md article URLs to canonical trailing-slash pages."""
    articles_dir = site_dir / "articles"
    if not articles_dir.is_dir():
        return
    for page_dir in sorted(articles_dir.iterdir()):
        if not page_dir.is_dir() or not (page_dir / "index.html").is_file():
            continue
        slug = page_dir.name
        if slug in {"index", "sitemap"}:
            continue
        target = f"{site_url}/articles/{slug}/"
        stub = articles_dir / f"{slug}.md"
        stub.write_text(
            f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="refresh" content="0; url={html.escape(target, quote=True)}">
  <link rel="canonical" href="{html.escape(target, quote=True)}">
  <script>location.replace({target!r});</script>
  <title>Redirecting…</title>
</head>
<body>
  <p>Moved to <a href="{html.escape(target, quote=True)}">{html.escape(target)}</a>.</p>
</body>
</html>
""",
            encoding="utf-8",
            newline="\n",
        )


def _canonical_url(site_dir: Path, html_path: Path, site_url: str) -> str:
    rel = html_path.relative_to(site_dir).as_posix()
    if rel.endswith("/index.html"):
        rel = rel[: -len("index.html")]
    elif rel == "index.html":
        rel = ""
    return f"{site_url}/{rel}"


def _noindex_urls(site_dir: Path, site_url: str) -> set[str]:
    found: set[str] = set()
    for html_path in site_dir.rglob("*.html"):
        try:
            head = html_path.read_bytes()[:16384]
        except OSError:
            continue
        if NOINDEX_RE.search(head):
            found.add(_canonical_url(site_dir, html_path, site_url))
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
    today = date.today().isoformat()
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for loc in urls:
        lines.extend(
            [
                "  <url>",
                f"    <loc>{html.escape(loc, quote=True)}</loc>",
                f"    <lastmod>{today}</lastmod>",
                "  </url>",
            ]
        )
    lines.append("</urlset>")
    lines.append("")
    sitemap.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def _write_html_sitemap(site_dir: Path, site_url: str, urls: list[str]) -> None:
    page_dir = site_dir / "sitemap"
    page_dir.mkdir(exist_ok=True)
    items = "\n".join(
        f'    <li><a href="{html.escape(url, quote=True)}">{html.escape(url)}</a></li>'
        for url in urls
    )
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Sitemap - Kramlipi Docs</title>
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{site_url}/sitemap/">
  <link rel="sitemap" type="application/xml" title="Sitemap" href="{site_url}/sitemap.xml">
</head>
<body>
  <h1>Sitemap</h1>
  <p>XML sitemap for crawlers: <a href="{site_url}/sitemap.xml">{site_url}/sitemap.xml</a></p>
  <ul>
{items}
  </ul>
</body>
</html>
"""
    (page_dir / "index.html").write_text(page, encoding="utf-8", newline="\n")


def _remove_gz_sitemap(site_dir: Path) -> None:
    gz = site_dir / "sitemap.xml.gz"
    if gz.is_file():
        gz.unlink()
