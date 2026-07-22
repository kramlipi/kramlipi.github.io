# Fix GitHub Pages URL — root domain

Your site showed as `kramlipi.github.io/kramlipi` because the repo was named **`kramlipi`** (a *project* site).

To serve at **`https://kramlipi.github.io/`** (no `/kramlipi` path), the repo must be named **`kramlipi.github.io`**.

## Steps (5 minutes)

### 1. Rename on GitHub

1. Go to: https://github.com/kramlipi/kramlipi/settings  
2. **Repository name** → type: `kramlipi.github.io`  
3. Click **Rename**

GitHub redirects the old URL for a while; update remotes anyway.

### 2. Update local git remote

```bash
cd ~/karm/kramlip-docs
git remote set-url origin https://github.com/kramlipi/kramlipi.github.io.git
git remote -v
```

### 3. Confirm Pages source

https://github.com/kramlipi/kramlipi.github.io/settings/pages

- **Source:** GitHub Actions (not “Deploy from branch”)

### 4. Push (triggers redeploy)

```bash
git push origin main
```

Watch: https://github.com/kramlipi/kramlipi.github.io/actions

### 5. Open the site

| Page | URL |
|------|-----|
| Home | https://kramlipi.github.io/ |
| Get started | https://kramlipi.github.io/get-started/ |
| Commands | https://kramlipi.github.io/commands/ |

Wait 1–3 minutes after the workflow finishes.

## MkDocs config (already set)

`mkdocs.yml` uses:

```yaml
site_url: https://kramlipi.github.io/
```

This matches the org site root. No `/kramlipi/` prefix in links or sitemap after rename.

## If rename is not allowed

Alternatives:

1. **Custom domain** — add `docs/CNAME` with your domain; point DNS CNAME to `kramlipi.github.io`  
2. **New repo** — create empty `kramlipi.github.io`, push this code there, archive old `kramlipi` repo

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Still `/kramlipi/` in URL | Repo not renamed yet, or browser cache — hard refresh |
| 404 at root | Pages Source must be GitHub Actions; workflow must be green |
| Broken CSS | `site_url` must end with `/` → `https://kramlipi.github.io/` |
| Old links 404 | Update bookmarks from `/kramlipi/...` to `/...` |
