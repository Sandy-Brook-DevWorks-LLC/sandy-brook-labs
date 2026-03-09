# Sandy Brook ProjectLab

A static site showcasing Sandy Brook's internal product experiments and study guides. Sibling to the main Sandy Brook DevWorks site at `sandybrookdevworks.com` (source: `~/Repos/sandy-brook-web`).

## Stack

- Plain HTML, vanilla JS, Tailwind CSS v4 via CDN (`@tailwindcss/browser@4`)
- Google Fonts: Inter (body, weights 300–700), JetBrains Mono (code, weights 400, 600)
- No build step, no frameworks, no npm

## File Structure

| File / Directory | Purpose |
|------------------|---------|
| `index.html` | Main ProjectLab page (Relay, CogniWatch) |
| `styles/brand.css` | **Shared** — CSS custom properties, brand colors, grid bg, dark mode overrides |
| `styles/theme.js` | **Shared** — `toggleTheme()`, `toggleMenu()`, `closeMenu()` functions |
| `guides/index.html` | Guides hub page |
| `guides/content.css` | **Shared** — Content styling for all guide pages (typography, callouts, code blocks, tables, etc.) |
| `guides/linq/` | C# Data Structures & LINQ course (index + 5 lessons) |
| `blue_logo.jpg` | Light mode Sandy Brook logo |
| `dark_logo.jpg` | Dark mode Sandy Brook logo |
| `relay_logo.png` | Relay app icon |
| `cogniwatch_logo.png` | CogniWatch app icon |
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

1. **Navigation** — Sticky nav, logo, "Sandy Brook ProjectLab", links to Building/Shipped/Developers sections, dark mode toggle, mobile hamburger menu (bottom sheet)
2. **Hero** — Logo, badge, headline, subtitle
3. **Currently Building** — Dark section with Relay project card
4. **Past Projects** — CogniWatch project card with "Shipped" badge
5. **Footer** — Logo, Services/About/Contact links, copyright

### Guides (`guides/`)

- `guides/index.html` — Hub page listing all available guides
- `guides/linq/` — C# Data Structures & LINQ (5 lessons with Big-O cheat sheet)

Guide pages use `guides/content.css` for content styling. Content is wrapped in `<main>` so descendant selectors apply.

## Constraints

- No build step, no frameworks, no npm
- Tailwind CSS via CDN only
- Fully mobile responsive
- External links: `target="_blank" rel="noopener noreferrer"`
- Logo paths are relative to file depth (use `../../blue_logo.jpg` from `guides/linq/`)

## Main Site Reference

- Source: `~/Repos/sandy-brook-web`
- Domain: `sandybrookdevworks.com`
