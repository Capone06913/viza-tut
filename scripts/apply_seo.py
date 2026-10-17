# -*- coding: utf-8 -*-
"""Пишет canonical и robots в HTML, собирает sitemap.xml и robots.txt из seo/pages.json."""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "seo" / "pages.json"


def page_url(site_url: str, item: dict) -> str:
    base = site_url.rstrip("/") + "/"
    path = str(item.get("path") or "").lstrip("/")
    return base if not path else base + path


def robots_content(item: dict) -> str:
    if item.get("index", True):
        return "index, follow"
    return "noindex, follow"


def upsert_head(html: str, canonical: str, robots: str, title: str | None, description: str | None) -> str:
    html = re.sub(r'\n[ \t]*<link rel="canonical" href="[^"]*">', "", html)
    html = re.sub(r'\n[ \t]*<meta name="robots" content="[^"]*">', "", html)
    if title:
        html = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", html, count=1)
    if description is not None:
        if re.search(r'<meta name="description" content="', html):
            html = re.sub(
                r'<meta name="description" content="[^"]*">',
                f'<meta name="description" content="{description}">',
                html,
                count=1,
            )
        else:
            html = html.replace(
                "</title>",
                f'</title>\n  <meta name="description" content="{description}">',
                1,
            )
    block = (
        f'\n  <link rel="canonical" href="{canonical}">'
        f'\n  <meta name="robots" content="{robots}">'
    )
    marker = re.search(r'<meta name="description" content="[^"]*">', html)
    if marker:
        insert_at = marker.end()
    else:
        title_tag = re.search(r"</title>", html)
        if not title_tag:
            raise SystemExit("нет title")
        insert_at = title_tag.end()
    return html[:insert_at] + block + html[insert_at:]


def write_sitemap(site_url: str, pages: list[dict]) -> None:
    today = date.today().isoformat()
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for item in pages:
        if not item.get("index", True):
            continue
        loc = page_url(site_url, item)
        lines.append("  <url>")
        lines.append(f"    <loc>{loc}</loc>")
        lines.append(f"    <lastmod>{item.get('lastmod') or today}</lastmod>")
        lines.append(f"    <changefreq>{item.get('changefreq') or 'monthly'}</changefreq>")
        lines.append(f"    <priority>{item.get('priority') or '0.6'}</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_robots(site_url: str) -> None:
    sitemap = site_url.rstrip("/") + "/sitemap.xml"
    text = (
        "User-agent: *\n"
        "Allow: /\n"
        "\n"
        f"Sitemap: {sitemap}\n"
    )
    (ROOT / "robots.txt").write_text(text, encoding="utf-8")


def main() -> int:
    data = json.loads(PAGES.read_text(encoding="utf-8"))
    site_url = data["site_url"]
    pages = data["pages"]
    for item in pages:
        path = ROOT / item["file"]
        html = path.read_text(encoding="utf-8")
        html = upsert_head(
            html,
            page_url(site_url, item),
            robots_content(item),
            item.get("title"),
            item.get("description"),
        )
        path.write_text(html, encoding="utf-8")
    write_sitemap(site_url, pages)
    write_robots(site_url)
    indexed = sum(1 for item in pages if item.get("index", True))
    print(f"pages={len(pages)} indexed={indexed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
