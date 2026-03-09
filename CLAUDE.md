# Sandy Brook ProjectLab

A static site showcasing Sandy Brook's internal product experiments. Sibling to the main Sandy Brook DevWorks site at `sandybrookdevworks.com` (source: `~/Repos/sandy-brook-web`).

## Stack

- Plain HTML, vanilla JS, Tailwind CSS v4 via CDN (`@tailwindcss/browser@4`)
- Google Fonts: Inter (weights 300–700)
- No build step, no frameworks, no npm
- Single `index.html` file

## File Structure

| File                 | Purpose                                      |
|----------------------|----------------------------------------------|
| `index.html`         | Main (and only) page                         |
| `blue_logo.jpg`      | Light mode Sandy Brook logo                  |
| `dark_logo.jpg`      | Dark mode Sandy Brook logo                   |
| `relay_logo.png`     | Relay app icon (AI-generated)                |
| `cogniwatch_logo.png`| CogniWatch app icon                          |
| `CNAME`              | GitHub Pages custom domain (if configured)   |
| `.claude/launch.json`| Preview server config (python3 http.server)  |

## Design System (from sandy-brook-web)

### Brand Colors

| Token               | Value                        | Usage                                |
|----------------------|------------------------------|--------------------------------------|
| `--brand-teal`       | `#1a5f6b`                    | Primary brand color (light mode)     |
| `--brand-teal-light` | `#2d8291`                    | Brand color in dark mode contexts    |
| `--brand-teal-dark`  | `#12444d`                    | Darker accent                        |
| `--color-brand-shadow` | `rgba(26, 95, 107, 0.25)` | Box-shadow on CTAs                   |

### Tailwind Theme Extension

```css
@theme {
    --color-brand: var(--brand-teal);
    --color-brand-light: var(--brand-teal-light);
    --color-brand-dark: var(--brand-teal-dark);
    --color-brand-shadow: rgba(26, 95, 107, 0.25);
}
```

### Surface Colors (Tailwind defaults)

| Context       | Light Mode        | Dark Mode          |
|---------------|-------------------|--------------------|
| Body bg       | `bg-slate-50`     | `dark:bg-slate-950`|
| Body text     | `text-slate-900`  | `dark:text-slate-50`|
| Card bg       | `bg-white`        | `dark:bg-slate-950` or `dark:bg-slate-900` |
| Muted text    | `text-slate-600`  | `dark:text-slate-400`|
| Borders       | `border-slate-200`| `dark:border-slate-800`|
| Nav bg        | `bg-white/80 backdrop-blur-md` | `dark:bg-slate-950/80` |

### Typography

- Font family: `'Inter', system-ui, -apple-system, sans-serif`
- Headings: `font-bold` / `font-extrabold`, `tracking-tight`
- Body: default weight (400), `leading-relaxed` for paragraphs
- Small labels: `text-xs font-medium tracking-widest uppercase`

### Spacing & Layout Patterns

- Container: `container mx-auto px-4`
- Section padding: `py-24` (desktop), responsive via Tailwind
- Cards: `rounded-2xl border p-8`, hover effect: `hover:border-brand/50 hover:shadow-2xl hover:shadow-brand-shadow/20`
- Nav height: `h-16`
- App icon sizing: `w-24 md:w-48` with `aspect-square rounded-2xl overflow-hidden`

### Custom Utility Classes

```css
.hover-bg-brand:hover { background-color: var(--brand-teal-light); }
.dark .hover-bg-brand:hover { background-color: var(--brand-teal); }
.dark .text-brand { color: var(--brand-teal-light); }
.dark .bg-brand { background-color: var(--brand-teal-light); }
.dark .border-brand { border-color: var(--brand-teal-light); }
```

### Background Grid Pattern

Subtle SVG grid overlay on the page background:

```css
.bg-grid-slate-100 {
    background-image: url("data:image/svg+xml,...");
}
```

Applied via: `<div class="fixed inset-0 bg-grid-slate-100 [mask-image:linear-gradient(0deg,white,rgba(255,255,255,0.6))] -z-10 pointer-events-none"></div>`

## Logo Rendering Pattern

```html
<img src="blue_logo.jpg" alt="..." class="... dark:hidden shadow-sm">
<img src="dark_logo.jpg" alt="..." class="hidden ... dark:block shadow-sm">
```

Favicon: `<link rel="icon" type="image/jpeg" href="blue_logo.jpg">`

## Dark Mode Implementation

Class-based dark mode using Tailwind v4's `@custom-variant`:

```css
@custom-variant dark (&:where(.dark, .dark *));
```

Toggle logic (vanilla JS in `<head>` to avoid FOUC) uses `localStorage.theme` and `prefers-color-scheme` media query.

## Site Structure (index.html)

1. **Navigation** — Sticky nav with logo, "Sandy Brook ProjectLab" branding, links to main site sections (Building, Shipped), dark mode toggle
2. **Hero** — Logo, animated badge, headline "Ideas in Motion. Projects in Progress.", subtitle
3. **Currently Building** — Dark section (`bg-slate-900`) with card (`bg-slate-800`). Relay project with "In Development" badge, app icon between subtitle and description
4. **Past Projects** — Default page background. CogniWatch project with "Shipped" badge, app icon between subtitle and description, "Visit Landing Page" link
5. **Footer** — Logo, nav links to main site (Services, About, Contact), copyright

## Project Content

### Currently Building

- **Relay** — AI Phone Assistant
  - Status: In Development
  - Tags: AI, Voice, Telephony, NLP
  - No external link yet

### Past Projects

- **CogniWatch** — AI Conversations on Your Wrist
  - Status: Shipped
  - Tags: Apple Watch, iOS, AI, Voice
  - Landing page: https://cogniwatch.sandybrook.io/

## Constraints

- No build step, no frameworks, no npm
- Tailwind CSS via CDN only
- Must be fully mobile responsive
- All external links open in new tabs (`target="_blank" rel="noopener noreferrer"`)
- Dark mode must match the main site's implementation
- App icon pattern: small icon (`w-24 md:w-48`) placed between project subtitle and description

## Main Site Reference

- Source: `~/Repos/sandy-brook-web`
- Domain: `sandybrookdevworks.com`
