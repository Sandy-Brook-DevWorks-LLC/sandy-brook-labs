# Sandy Brook Projects Lab

A static site showcasing Sandy Brook's internal product experiments and study guides. Sibling to the main Sandy Brook DevWorks site at `sandybrookdevworks.com` (source: `~/Repos/sandy-brook-web`).

## Stack

- Plain HTML, vanilla JS, Tailwind CSS v4 via CDN (`@tailwindcss/browser@4`)
- Google Fonts: Inter (body, weights 300–700), JetBrains Mono (code, weights 400, 600)
- No build step, no frameworks, no npm

## File Structure

| File / Directory | Purpose |
|------------------|---------|
| `index.html` | Main Projects Lab page (Relay, KnowItOwl) |
| `styles/brand.css` | **Shared** — CSS custom properties, brand colors, grid bg, dark mode overrides |
| `styles/theme.js` | **Shared** — `toggleTheme()`, `toggleMenu()`, `closeMenu()` functions |
| `guides/index.html` | Guides hub page |
| `guides/content.css` | **Shared** — Content styling for all guide pages (typography, callouts, code blocks, tables, etc.) |
| `guides/linq/` | C# Data Structures & LINQ course (index + 5 lessons) |
| `blue_logo.jpg` | Light mode Sandy Brook logo |
| `dark_logo.jpg` | Dark mode Sandy Brook logo |
| `relay_logo.png` | Relay app icon |
| `cogniwatch_logo.png` | KnowItOwl app icon |
| `STYLE_GUIDE.md` | **Human-readable design system reference** with templates and how-to guides |
| `.claude/launch.json` | Preview server config (python3 http.server on port 8080) |

## Shared Assets

Three files eliminate duplication across all pages:

1. **`styles/brand.css`** — CSS variables (`--brand-teal`, `--font-sans`), body font stack, grid background SVGs, `.dark` utility overrides, mobile bottom sheet menu styles. Linked via `<link rel="stylesheet">`.

2. **`styles/theme.js`** — `toggleTheme()` for dark mode, `toggleMenu()`/`closeMenu()` for the mobile bottom sheet menu. Loaded via `<script src="...">` (no defer). Dark mode *init* is a 1-line inline `<script>` in each page's `<head>` to prevent FOUC.

3. **`guides/content.css`** — Content styling for guide pages. Targets elements inside `<main>` via descendant selectors (`main h1`, `main p`, etc.). Includes callout system (`.callout.tip/warn/danger`), code block styling, table styling, challenge boxes, page nav, syntax highlighting spans, Big-O badges.

Each HTML page also has a minimal inline `<style type="text/tailwindcss">` block (7 lines) for the Tailwind `@theme` and `@custom-variant` directives that the CDN requires inline.

## Design System

See `STYLE_GUIDE.md` for full details, copy-paste templates, and how-to guides.

### Brand Colors

| Token | Value | Usage |
|-------|-------|-------|
| `--brand-teal` | `#1a5f6b` | Primary accent (light mode) |
| `--brand-teal-light` | `#2d8291` | Dark mode accent, hover states |
| `--brand-teal-dark` | `#12444d` | Deep accents, shadows |

### Dark Mode

Class-based using `@custom-variant dark (&:where(.dark, .dark *))`. Toggle persists in `localStorage.theme`. Init script in `<head>` prevents flash.

### Surface Colors (Tailwind slate palette)

| Context | Light | Dark |
|---------|-------|------|
| Body bg | `bg-slate-50` | `dark:bg-slate-950` |
| Cards | `bg-white` | `dark:bg-slate-900` |
| Nav | `bg-white/80 backdrop-blur-md` | `dark:bg-slate-950/80` |
| Borders | `border-slate-200` | `dark:border-slate-800` |
| Muted text | `text-slate-600` | `dark:text-slate-400` |

## Site Structure

### Main Page (`index.html`)

1. **Navigation** — Sticky nav, logo, "Sandy Brook Projects Lab", links to Building/Shipped/Developers sections, dark mode toggle, mobile hamburger menu (bottom sheet)
2. **Hero** — Logo, badge, headline, subtitle
3. **Currently Building** — Dark section with Relay project card
4. **Past Projects** — KnowItOwl project card with "Shipped" badge
5. **Footer** — Logo, Services/About/Contact links, copyright

### Guides (`guides/`)

- `guides/index.html` — Hub page listing all available guides
- `guides/linq/` — C# Data Structures & LINQ (5 lessons with Big-O cheat sheet)

Guide pages use `guides/content.css` for content styling. Content is wrapped in `<main>` so descendant selectors apply.

### ASP.NET Core Study Guide (`guides/asp-net-core-principles/`)

A 36-chapter study guide based on "ASP.NET Core in Action, 3rd Edition" plus a RecipeVault capstone project. Designed for interview preparation.

| File | Purpose |
|------|---------|
| `index.html` | Landing page with all 5 parts and chapter cards |
| `chapter01.html` – `chapter36.html` | One page per book chapter with summary, code examples, and 10-question quiz |
| `capstone.html` | RecipeVault guided project tying all concepts together |
| `crypto.js` | Client-side AES-256-GCM decryption + password prompt UI |
| `encrypt_guide.py` | Python script to encrypt all page content for publishing |
| `decrypt_guide.py` | Python script to decrypt all page content for editing |

#### Content Protection

The `<main>` content of every guide page is encrypted with AES-256-GCM. The page source contains only the nav shell, footer, and an encrypted blob. Visitors must enter the password to view content. The password is cached in `sessionStorage` so it only needs to be entered once per browser session.

**Encryption uses:** PBKDF2 (100,000 iterations, SHA-256) for key derivation, AES-256-GCM for encryption. Implemented with the Web Crypto API on the browser side and Python `cryptography` library for the build scripts.

#### Editing Workflow

The guide pages toggle between two states: **encrypted** (for publishing) and **decrypted** (for editing). You must decrypt before making content changes, then re-encrypt before publishing.

```bash
# Step 1: Decrypt all pages so you can edit them
cd guides/asp-net-core-principles
python decrypt_guide.py <password>

# Step 2: Make your edits to any HTML file(s)...
#   - Content lives inside <main> tags
#   - Use the same HTML patterns as existing chapters
#   - See STYLE_GUIDE.md for callout, code block, and quiz templates

# Step 3: Re-encrypt all pages for publishing
python encrypt_guide.py <password>
```

Both scripts require the `cryptography` Python package (auto-installs if missing). They process all `chapter*.html`, `index.html`, and `capstone.html` in the guide folder. Files that are already in the target state are skipped automatically.

**Important:** The password is not stored anywhere in the repository. You must know it to decrypt or re-encrypt. If you encrypt with a different password, the old `crypto.js` session cache won't work — visitors will simply be re-prompted.

#### Chapter Structure

Every chapter page follows a consistent template: `<head>` with Tailwind CDN + Google Fonts + brand.css + content.css, sticky nav with chapter links for the current part, mobile menu, `<main>` with content sections using `h2`/`h3` headings, syntax-highlighted code blocks (`.kw`, `.tp`, `.str`, `.fn`, `.cm`, `.num` spans), callout boxes (`.callout.tip`, `.callout.warn`, `.callout.danger`), a 10-question quiz using `<details>/<summary>` for expandable answers, and a `.page-nav` div with Previous/Next links. The nav bar shows abbreviated chapter links for the current book part (e.g., C1–C7 for Part 1 chapters).

## Constraints

- No build step, no frameworks, no npm
- Tailwind CSS via CDN only
- Fully mobile responsive
- External links: `target="_blank" rel="noopener noreferrer"`
- Logo paths are relative to file depth (use `../../blue_logo.jpg` from `guides/linq/`)

## Main Site Reference

- Source: `~/Repos/sandy-brook-web`
- Domain: `sandybrookdevworks.com`
