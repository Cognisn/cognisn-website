# Blog Publishing Guide

## Creating a New Post

1. Create a new Markdown file in `blog/posts/`:

   ```
   blog/posts/your-article-slug.md
   ```

   The filename becomes the URL slug — e.g. `my-new-article.md` becomes `/blog/my-new-article.html`.

2. Add YAML frontmatter at the top of the file:

   ```markdown
   ---
   title: Your Article Title
   date: 2026-04-10
   description: A one or two sentence summary for SEO and social sharing. This is also what appears on the blog listing cards.
   tags:
     - Python
     - Open Source
   ---
   ```

   | Field         | Required | Description                                                  |
   |---------------|----------|--------------------------------------------------------------|
   | `title`       | Yes      | Article title (shown on page and in browser tab)             |
   | `date`        | Yes      | Publication date in `YYYY-MM-DD` format                      |
   | `description` | Yes      | Short summary for SEO meta tags, social sharing, and listing |
   | `tags`        | No       | List of topic tags displayed on the article and listing cards |
   | `author`      | No       | Defaults to "Matthew Westwood-Hill" if omitted               |

3. Write your article content in standard Markdown below the frontmatter:

   ```markdown
   ---
   title: Getting Started with Konfig
   date: 2026-04-15
   description: A walkthrough of setting up Konfig for settings, secrets, and logging in your Python project.
   tags:
     - Python
     - Konfig
     - Tutorial
   ---

   Intro paragraph — this is what you'd use as the LinkedIn post summary.
   Keep it punchy and link back to the full article.

   ## Section Heading

   Regular paragraph text with **bold**, *italic*, and [links](https://example.com).

   ### Sub-section

   - Bullet list item
   - Another item

   ```python
   # Fenced code blocks with syntax highlighting
   from konfig import AppContext

   with AppContext(name="demo", version="1.0.0") as ctx:
       host = ctx.settings.get("db.host", "localhost")
   ```

   > Blockquotes for emphasis or attribution.

   Images can be included from the `images/` directory:

   ![Alt text](/images/my-screenshot.png)
   ```

## Supported Markdown Features

- Headings (`## H2`, `### H3`, etc.)
- Bold, italic, strikethrough
- Links (internal and external)
- Ordered and unordered lists
- Fenced code blocks with language hints
- Blockquotes
- Tables
- Images
- Inline code

## Building Locally

Run the build script to generate HTML from your Markdown posts:

```bash
pip install -r requirements.txt   # first time only
python3 build.py
```

The script will:
- Convert each `.md` file in `blog/posts/` to a full HTML article in `blog/`
- Regenerate `blog/index.html` with all posts listed newest-first
- Update the "From the Blog" section on the home page (latest 3 posts)
- Remove any orphaned `.html` files for deleted posts

Preview locally by opening the generated HTML files in a browser, or use a local server:

```bash
python3 -m http.server 8000
```

Then visit `http://localhost:8000`.

## Publishing

Commit your new `.md` file and push to the `develop` branch (or `main` for production):

```bash
git add blog/posts/my-new-article.md
git commit -m "Add blog post: My New Article"
git push
```

Netlify runs `build.py` automatically on deploy — the HTML generation happens server-side. You only commit the Markdown source files, not the generated HTML.

## LinkedIn Workflow

1. Write the full article as a Markdown post (as above)
2. Push to publish it on the site
3. On LinkedIn, write a short intro (2–3 sentences from the `description`) and link to the full article:
   ```
   https://cognisn.com/blog/your-article-slug.html
   ```
4. The Open Graph meta tags will automatically generate a rich link preview with the title and description

## Comments & Reactions (giscus)

Blog articles include a comments and reactions section powered by [giscus](https://giscus.app), which uses GitHub Discussions as the backend.

To complete the setup:
1. Install the [giscus GitHub App](https://github.com/apps/giscus) on the `Cognisn/cognisn-website` repository
2. Visit https://giscus.app and enter `Cognisn/cognisn-website`
3. Copy the `data-repo-id` and `data-category-id` values
4. Update the constants in `build.py`:
   ```python
   GISCUS_REPO_ID = "your-repo-id"
   GISCUS_CATEGORY_ID = "your-category-id"
   ```
5. Rebuild and push — comments will appear on all articles

## File Structure

```
blog/
├── posts/                  # Markdown source files (you write these)
│   ├── welcome-to-cognisn.md
│   └── my-new-article.md
├── index.html              # Auto-generated listing page
├── welcome-to-cognisn.html # Auto-generated article page
└── my-new-article.html     # Auto-generated article page
```
