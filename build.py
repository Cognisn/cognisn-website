#!/usr/bin/env python3
"""
Cognisn Blog Builder

Converts Markdown posts in blog/posts/ to HTML articles, generates the blog
listing page (blog/index.html) and updates the home page "From the Blog" section.

Usage:
    python3 build.py

Post format (blog/posts/my-article.md):
    ---
    title: My Article Title
    date: 2026-04-05
    description: A short summary for SEO and social sharing.
    tags:
      - Python
      - Open Source
    ---

    Article content in Markdown...

The filename (minus .md) becomes the URL slug: /blog/my-article.html
"""

import os
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    import markdown
    import yaml
except ImportError:
    print("Installing dependencies...")
    os.system(f"{sys.executable} -m pip install -q markdown pyyaml")
    import markdown
    import yaml


# ── Paths ─────────────────────────────────────────────────────────────────

ROOT = Path(__file__).parent
POSTS_DIR = ROOT / "blog" / "posts"
BLOG_OUT_DIR = ROOT / "blog"
INDEX_HTML = ROOT / "index.html"
BLOG_INDEX_HTML = BLOG_OUT_DIR / "index.html"

SITE_URL = "https://cognisn.com"


# ── Giscus config ────────────────────────────────────────────────────────
# Visit https://giscus.app to get your repo-id and category-id,
# then update these values.

GISCUS_REPO = "Cognisn/cognisn-website"
GISCUS_REPO_ID = "R_kgDOR1K7rQ"
GISCUS_CATEGORY = "General"
GISCUS_CATEGORY_ID = "DIC_kwDOR1K7rc4C6GqH"


# ── Shared HTML fragments ────────────────────────────────────────────────

FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
           "viewBox='0 0 130 130'%3E%3Crect width='130' height='130' rx='28' "
           "fill='%23080e1e'/%3E%3Cdefs%3E%3ClinearGradient id='a' x1='0' "
           "y1='0' x2='1' y2='1'%3E%3Cstop offset='0%25' stop-color="
           "'%233a78c4'/%3E%3Cstop offset='50%25' stop-color='%235aaae8'/%3E"
           "%3Cstop offset='100%25' stop-color='%233a78c4'/%3E%3C/"
           "linearGradient%3E%3CradialGradient id='b' cx='40%25' cy='35%25' "
           "r='60%25'%3E%3Cstop offset='0%25' stop-color='%237ac0f8'/%3E"
           "%3Cstop offset='100%25' stop-color='%234a90d8'/%3E%3C/"
           "radialGradient%3E%3C/defs%3E%3Cg transform='translate(65,65)'"
           "%3E%3Cpath d='M32-48A48 48 0 1 0 32 48' stroke='url(%23a)' "
           "stroke-width='4' fill='none' stroke-linecap='round'/%3E%3Ccircle "
           "cx='32' cy='-48' r='5' fill='%236ab8f0'/%3E%3Ccircle cx='32' "
           "cy='48' r='5' fill='%235aaae8' opacity='.85'/%3E%3Ccircle "
           "cx='12' cy='0' r='9' fill='url(%23b)'/%3E%3Ccircle cx='12' "
           "cy='0' r='4.5' fill='%23a0d8ff' opacity='.9'/%3E%3C/g%3E%3C/"
           "svg%3E")

NAV_LOGO = '''<svg width="110" height="28" viewBox="0 0 440 110" fill="none" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="arc-n" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="#3a78c4"/>
            <stop offset="50%" stop-color="#5aaae8"/>
            <stop offset="100%" stop-color="#3a78c4"/>
        </linearGradient>
        <radialGradient id="dot-n" cx="40%" cy="35%" r="60%">
            <stop offset="0%" stop-color="#7ac0f8"/>
            <stop offset="100%" stop-color="#4a90d8"/>
        </radialGradient>
    </defs>
    <g transform="translate(55,55)">
        <line x1="-55" y1="0" x2="-36" y2="0" stroke="#4a8abf" stroke-width="0.7" opacity="0.3"/>
        <line x1="36" y1="0" x2="80" y2="0" stroke="#4a8abf" stroke-width="0.7" opacity="0.15"/>
        <line x1="0" y1="0" x2="26" y2="-33" stroke="#4a8abf" stroke-width="0.7" opacity="0.22"/>
        <line x1="0" y1="0" x2="26" y2="33" stroke="#4a8abf" stroke-width="0.7" opacity="0.22"/>
        <path d="M25 -38 A38 38 0 1 0 25 38" stroke="url(#arc-n)" stroke-width="3" fill="none" stroke-linecap="round"/>
        <circle cx="25" cy="-38" r="3.5" fill="#6ab8f0"/>
        <circle cx="25" cy="38" r="3.5" fill="#5aaae8" opacity="0.85"/>
        <circle cx="10" cy="0" r="7" fill="url(#dot-n)"/>
        <circle cx="10" cy="0" r="3.5" fill="#a0d8ff" opacity="0.9"/>
    </g>
    <text x="108" y="70" font-family="'Syne', sans-serif" font-weight="600" font-size="54" fill="#5a9fd4" letter-spacing="-0.5">cognisn</text>
</svg>'''


def nav_html(active=""):
    """Generate the site navigation bar."""
    def link(href, label, key):
        cls = ' class="active"' if active == key else ''
        return f'<li><a href="{href}"{cls}>{label}</a></li>'

    return f'''<nav class="site-nav">
    <div class="container">
        <a href="/" class="site-nav__brand">{NAV_LOGO}</a>
        <button class="site-nav__toggle" aria-label="Toggle navigation">&#9776;</button>
        <ul class="site-nav__links">
            {link("/", "Home", "home")}
            {link("/projects.html", "Projects", "projects")}
            {link("/blog/", "Blog", "blog")}
            {link("/about.html", "About", "about")}
            {link("/contact.html", "Contact", "contact")}
        </ul>
    </div>
</nav>'''


FOOTER = '''<footer class="site-footer">
    <div class="container">
        &copy; 2026 Cognisn. All rights reserved.
    </div>
</footer>'''


# ── Post parsing ──────────────────────────────────────────────────────────

def parse_post(filepath):
    """Parse a Markdown file with YAML frontmatter."""
    text = filepath.read_text(encoding="utf-8")

    # Split frontmatter from body
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', text, re.DOTALL)
    if not match:
        print(f"  SKIP {filepath.name} — no frontmatter found")
        return None

    meta = yaml.safe_load(match.group(1))
    body_md = match.group(2)

    # Convert Markdown to HTML
    md = markdown.Markdown(extensions=["fenced_code", "codehilite", "tables", "toc"])
    body_html = md.convert(body_md)

    # Derive slug from filename
    slug = filepath.stem

    # Parse date
    date_raw = meta.get("date", "")
    if isinstance(date_raw, datetime):
        date_obj = date_raw
    elif isinstance(date_raw, str):
        date_obj = datetime.strptime(date_raw, "%Y-%m-%d")
    else:
        date_obj = datetime.now()

    return {
        "title": meta.get("title", slug),
        "description": meta.get("description", ""),
        "date": date_obj,
        "date_display": date_obj.strftime("%-d %B %Y"),
        "date_iso": date_obj.strftime("%Y-%m-%d"),
        "tags": meta.get("tags", []),
        "slug": slug,
        "url": f"/blog/{slug}.html",
        "body_html": body_html,
        "author": meta.get("author", "Matthew Westwood-Hill"),
    }


# ── HTML generators ───────────────────────────────────────────────────────

def generate_article_html(post):
    """Generate a full HTML page for a blog article."""
    tags_html = "".join(f'<span class="tag">{t}</span>' for t in post["tags"])

    og_image = f'<meta property="og:image" content="{SITE_URL}/images/og-card.png">'

    giscus_html = ""
    if GISCUS_REPO_ID and GISCUS_CATEGORY_ID:
        giscus_html = f'''
            <hr>
            <div class="article__comments">
                <h2 class="section-title" style="font-size: 1.25rem; margin-bottom: 1.5rem;">Comments &amp; Reactions</h2>
                <script src="https://giscus.app/client.js"
                    data-repo="{GISCUS_REPO}"
                    data-repo-id="{GISCUS_REPO_ID}"
                    data-category="{GISCUS_CATEGORY}"
                    data-category-id="{GISCUS_CATEGORY_ID}"
                    data-mapping="pathname"
                    data-strict="0"
                    data-reactions-enabled="1"
                    data-emit-metadata="0"
                    data-input-position="top"
                    data-theme="transparent_dark"
                    data-lang="en"
                    data-loading="lazy"
                    crossorigin="anonymous"
                    async>
                </script>
            </div>'''

    return f'''<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{post["title"]} — Cognisn Blog</title>
    <meta name="description" content="{post["description"]}">

    <meta property="og:title" content="{post["title"]}">
    <meta property="og:description" content="{post["description"]}">
    <meta property="og:type" content="article">
    <meta property="og:url" content="{SITE_URL}{post["url"]}">
    {og_image}

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
    <link rel="icon" type="image/svg+xml" href="{FAVICON}">
    <link rel="stylesheet" href="../css/theme.css">
    <link rel="stylesheet" href="../css/site.css">
</head>
<body>

    {nav_html("blog")}

    <main>
        <article class="article">
            <header class="article__header">
                <p class="section-label"><a href="/blog/" style="color: inherit; text-decoration: none;">&larr; Blog</a></p>
                <h1 class="article__title">{post["title"]}</h1>
                <div class="article__meta">
                    <span>{post["date_display"]}</span>
                    <span>{post["author"]}</span>
                </div>
                {f'<div class="card__tags" style="margin-top: 0.75rem;">{tags_html}</div>' if tags_html else ""}
            </header>

            <div class="article__body">
                {post["body_html"]}
            </div>

            {giscus_html}

            <hr>
            <div style="display: flex; gap: 0.75rem; flex-wrap: wrap;">
                <a href="/blog/" class="btn btn-outline">&larr; All Articles</a>
            </div>
        </article>
    </main>

    {FOOTER}
    <script src="../js/site.js"></script>
</body>
</html>'''


def generate_blog_card(post):
    """Generate a card for the blog listing."""
    tags_html = "".join(f'<span class="tag">{t}</span>' for t in post["tags"])
    return f'''<div class="card">
    <div class="card__meta" style="margin-bottom: 0.75rem;">
        <span>{post["date_display"]}</span>
    </div>
    <h3 class="card__title"><a href="{post["url"]}">{post["title"]}</a></h3>
    <p class="card__desc">{post["description"]}</p>
    {f'<div class="card__tags">{tags_html}</div>' if tags_html else ""}
</div>'''


def generate_blog_index(posts):
    """Generate the blog listing page."""
    if posts:
        cards = "\n".join(generate_blog_card(p) for p in posts)
    else:
        cards = '''<div class="card">
    <p class="card__desc" style="color: var(--app-text-muted); font-style: italic;">Articles coming soon. Follow on LinkedIn for updates.</p>
</div>'''

    return f'''<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blog — Cognisn</title>
    <meta name="description" content="Articles, announcements, and technical writing from Cognisn.">

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
    <link rel="icon" type="image/svg+xml" href="{FAVICON}">
    <link rel="stylesheet" href="../css/theme.css">
    <link rel="stylesheet" href="../css/site.css">
</head>
<body>

    {nav_html("blog")}

    <main>
        <section>
            <div class="container">
                <p class="section-label">Blog</p>
                <h1 class="section-title">Articles &amp; Announcements</h1>
                <p class="section-subtitle">Technical writing, project updates, and thoughts on software development.</p>

                <div class="card-grid">
                    {cards}
                </div>
            </div>
        </section>
    </main>

    {FOOTER}
    <script src="../js/site.js"></script>
</body>
</html>'''


def update_home_page(posts):
    """Update the 'From the Blog' section on the home page."""
    if not INDEX_HTML.exists():
        print("  SKIP home page update — index.html not found")
        return

    html = INDEX_HTML.read_text(encoding="utf-8")

    # Build the replacement cards (show latest 3)
    latest = posts[:3]
    if latest:
        cards = "\n                    ".join(generate_blog_card(p) for p in latest)
    else:
        cards = '''<div class="card">
                        <p class="card__desc" style="color: var(--app-text-muted); font-style: italic;">Articles coming soon. Follow on <a href="https://www.linkedin.com/in/mattheww3/" target="_blank" rel="noopener">LinkedIn</a> for updates.</p>
                    </div>'''

    # Replace the blog section content between markers
    pattern = r'(<!-- Latest from the blog -->\s*<section>\s*<div class="container">\s*<p class="section-label">Latest</p>\s*<h2 class="section-title">From the Blog</h2>\s*<p class="section-subtitle">Thoughts, announcements, and technical deep-dives\.</p>\s*<div class="card-grid">)\s*(.*?)\s*(</div>\s*</div>\s*</section>)'

    replacement = rf'\1\n                    {cards}\n                \3'

    new_html, count = re.subn(pattern, replacement, html, flags=re.DOTALL)

    if count > 0:
        INDEX_HTML.write_text(new_html, encoding="utf-8")
        print(f"  Updated home page with {len(latest)} latest post(s)")
    else:
        print("  SKIP home page — blog section marker not found")


def update_sitemap(posts):
    """Append blog post URLs to sitemap.xml."""
    sitemap_path = ROOT / "sitemap.xml"
    if not sitemap_path.exists():
        return

    xml = sitemap_path.read_text(encoding="utf-8")

    # Remove any existing blog post entries (between markers)
    xml = re.sub(r'\n  <!-- blog posts -->.*?<!-- /blog posts -->', '', xml, flags=re.DOTALL)

    # Remove closing tag, we'll re-add it
    xml = xml.replace('</urlset>', '').rstrip()

    # Add blog post entries
    entries = '\n  <!-- blog posts -->'
    for post in posts:
        entries += f'''
  <url>
    <loc>{SITE_URL}{post["url"]}</loc>
    <lastmod>{post["date_iso"]}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>'''
    entries += '\n  <!-- /blog posts -->'

    xml += entries + '\n</urlset>\n'
    sitemap_path.write_text(xml, encoding="utf-8")
    print(f"  Updated sitemap with {len(posts)} blog post(s)")


# ── Main ──────────────────────────────────────────────────────────────────

def build():
    print("Building blog...")

    # Find all markdown posts
    if not POSTS_DIR.exists():
        POSTS_DIR.mkdir(parents=True, exist_ok=True)
        print(f"  Created {POSTS_DIR}")

    md_files = sorted(POSTS_DIR.glob("*.md"))
    print(f"  Found {len(md_files)} post(s)")

    # Parse all posts
    posts = []
    for f in md_files:
        post = parse_post(f)
        if post:
            posts.append(post)

    # Sort by date descending (newest first)
    posts.sort(key=lambda p: p["date"], reverse=True)

    # Generate article pages
    for post in posts:
        out_path = BLOG_OUT_DIR / f"{post['slug']}.html"
        out_path.write_text(generate_article_html(post), encoding="utf-8")
        print(f"  Built {out_path.relative_to(ROOT)}")

    # Generate blog listing
    BLOG_INDEX_HTML.write_text(generate_blog_index(posts), encoding="utf-8")
    print(f"  Built {BLOG_INDEX_HTML.relative_to(ROOT)}")

    # Update home page
    update_home_page(posts)

    # Clean up old sample article if it exists
    sample = BLOG_OUT_DIR / "sample-article.html"
    if sample.exists() and not (POSTS_DIR / "sample-article.md").exists():
        sample.unlink()
        print("  Removed orphaned sample-article.html")

    # Update sitemap with blog posts
    update_sitemap(posts)

    print(f"Done — {len(posts)} article(s) published")


if __name__ == "__main__":
    build()
