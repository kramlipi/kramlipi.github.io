# Kramlipi Docs

Documentation for **code-agent** — built with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/).

All pages live at the site root (no `/kramlipi-ai-code-agent/` prefix):

| Page | URL |
|------|-----|
| Home | https://kramlipi.github.io/ |
| Quick Start | https://kramlipi.github.io/quick-start/ |
| Commands | https://kramlipi.github.io/commands/ |
| Experts | https://kramlipi.github.io/experts/ |

## Features

- **Full-text search** (`Ctrl+K`)
- **SEO** — meta tags, sitemap, social cards
- **Dark / light mode**

## Quick start (local)

```bash
cd ~/karm/kramlip-docs
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
mkdocs serve
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Build

```bash
mkdocs build
# output: site/
```

## Deploy to GitHub Pages

This repo deploys automatically on every push to `main`.

### Why the URL was `/kramlipi/` (and how to fix it)

GitHub serves docs at the **repo root** only when the repository is named:

```text
kramlipi.github.io
```

| Repo name on GitHub | Public URL |
|---------------------|------------|
| `kramlipi` (project site) | `https://kramlipi.github.io/kramlipi/` |
| `kramlipi.github.io` (org site) | `https://kramlipi.github.io/` |

**One-time fix — rename the repo:**

1. Open **https://github.com/kramlipi/kramlipi/settings**
2. **Repository name** → change to `kramlipi.github.io` → **Rename**
3. Update your local remote:

   ```bash
   cd ~/karm/kramlip-docs
   git remote set-url origin https://github.com/kramlipi/kramlipi.github.io.git
   ```

4. Push again — Actions redeploys to the root URL

### GitHub Pages settings

1. Open **https://github.com/kramlipi/kramlipi.github.io/settings/pages** (after rename)
2. **Build and deployment** → **Source** → **GitHub Actions**
3. Push to `main` or run **Deploy documentation to GitHub Pages** manually

### Live URL

**https://kramlipi.github.io/**

Quick start: **https://kramlipi.github.io/quick-start/**

### Custom domain (optional)

1. Add a `CNAME` file in `docs/` with your domain (e.g. `docs.kramlipi.dev`)
2. Update `site_url` in `mkdocs.yml` to match
3. Configure DNS at your registrar (CNAME → `kramlipi.github.io`)
4. Enable **Enforce HTTPS** in GitHub Pages settings

## Add pages

Edit files under `docs/` and add to `nav:` in `mkdocs.yml`.
