# Sandy Brook ProjectLab — Style Guide

A reference for anyone adding pages or guides to the Sandy Brook ProjectLab site.

## Stack

- **HTML** — Static pages, no build step, no frameworks
- **Tailwind CSS v4** — Via CDN (`@tailwindcss/browser@4`)
- **Google Fonts** — Inter (body), JetBrains Mono (code)
- **Dark mode** — Class-based (`.dark` on `<html>`), persisted in `localStorage`

## Shared Files

| File | Purpose |
|------|---------|
| `styles/brand.css` | CSS custom properties (brand colors, fonts), grid background, dark mode utility overrides |
| `styles/theme.js` | `toggleTheme()` function for the dark mode button |
| `guides/content.css` | Content styling for guide pages: typography, callouts, code blocks, tables, challenge boxes, page nav, syntax highlighting |

## Color Palette

| Token | Light | Dark | Usage |
|-------|-------|------|-------|
| `--brand-teal` | `#1a5f6b` | — | Primary accent, headings, links |
| `--brand-teal-light` | `#2d8291` | — | Dark mode accent, hover states |
| `--brand-teal-dark` | `#12444d` | — | Shadows, deep accents |
| Tailwind `brand` | `#1a5f6b` | `#2d8291` | Use as `text-brand`, `bg-brand`, `border-brand` |

Surface colors use Tailwind's `slate` palette:
- **Light**: `bg-slate-50` (page), `bg-white` (cards/nav)
- **Dark**: `bg-slate-950` (page), `bg-slate-900` (cards), `bg-slate-800` (surfaces)

## `<head>` Template

Every page needs these in `<head>`. Adjust paths based on file depth.

```html
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page Title</title>
    <meta name="description" content="Page description.">
    <link rel="icon" type="image/jpeg" href="[depth]blue_logo.jpg">
    <link rel="apple-touch-icon" href="[depth]blue_logo.jpg">

    <!-- Tailwind CSS v4 CDN -->
    <script src="https://unpkg.com/@tailwindcss/browser@4"></script>

    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <!-- Add JetBrains Mono if the page has code blocks: -->
    <!-- &family=JetBrains+Mono:wght@400;600 -->

    <!-- Shared styles -->
    <link rel="stylesheet" href="[depth]styles/brand.css">
    <!-- Add for guide pages only: -->
    <!-- <link rel="stylesheet" href="[depth]guides/content.css"> -->

    <!-- Tailwind theme (must be inline for CDN processing) -->
    <style type="text/tailwindcss">
        @theme {
            --color-brand: var(--brand-teal);
            --color-brand-light: var(--brand-teal-light);
            --color-brand-dark: var(--brand-teal-dark);
            --color-brand-shadow: rgba(26, 95, 107, 0.25);
        }
        @custom-variant dark (&:where(.dark, .dark *));
    </style>

    <!-- Dark mode (inline init prevents flash, external file adds toggle) -->
    <script>
        if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) document.documentElement.classList.add('dark')
    </script>
    <script src="[depth]styles/theme.js"></script>
</head>
```

**Depth prefixes:**

| File location | `[depth]` |
|---------------|-----------|
| Root (`index.html`) | _(empty)_ |
| `guides/` | `../` |
| `guides/linq/` | `../../` |

## `<body>` Template

```html
<body class="bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-50 transition-colors duration-300 min-h-screen flex flex-col">
    <!-- Grid background -->
    <div class="fixed inset-0 bg-grid-slate-100 [mask-image:linear-gradient(0deg,white,rgba(255,255,255,0.6))] -z-10 pointer-events-none"></div>

    <!-- Navigation (see below) -->
    <!-- Page content -->
    <!-- Footer (see below) -->
</body>
```

## Navigation Template

The nav adapts per page. Key parameters: logo path, subtitle text, nav links.

```html
<nav class="sticky top-0 z-50 w-full border-b border-slate-200/40 bg-white/80 backdrop-blur-md dark:border-slate-800/40 dark:bg-slate-950/80">
    <div class="container mx-auto flex h-16 items-center justify-between px-4 md:px-6">
        <div class="flex items-center gap-4 font-bold text-xl tracking-tight">
            <a href="[home-path]" class="relative group" aria-label="Sandy Brook ProjectLab Home">
                <div class="absolute -inset-1 rounded-full bg-brand/20 blur opacity-0 group-hover:opacity-100 transition duration-500"></div>
                <img src="[depth]blue_logo.jpg" alt="Sandy Brook DevWorks Logo" class="relative h-12 w-12 rounded-full border border-slate-200 dark:hidden shadow-sm">
                <img src="[depth]dark_logo.jpg" alt="Sandy Brook DevWorks Logo" class="relative hidden h-12 w-12 rounded-full border border-slate-800 dark:block shadow-sm">
            </a>
            <div class="flex flex-col leading-tight">
                <span class="text-brand">[Title Line 1]</span>
                <span class="text-xs font-medium tracking-widest uppercase text-slate-500 dark:text-slate-400">[Title Line 2]</span>
            </div>
        </div>
        <div class="flex items-center gap-4 md:gap-8">
            <!-- Page-specific nav links here -->
            <button onclick="toggleTheme()" class="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors" aria-label="Toggle Theme">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="dark:hidden"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="hidden dark:block"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>
            </button>
        </div>
    </div>
</nav>
```

## Footer Template

```html
<footer class="border-t border-slate-200 dark:border-slate-800 py-12 mt-auto">
    <div class="container mx-auto px-4">
        <div class="flex flex-col md:flex-row justify-between items-center gap-8">
            <a href="[home-path]" class="flex items-center gap-3 font-bold text-xl group transition-transform hover:scale-105" aria-label="Sandy Brook ProjectLab Home">
                <img src="[depth]blue_logo.jpg" alt="Sandy Brook DevWorks Logo" class="h-8 w-8 rounded-full dark:hidden">
                <img src="[depth]dark_logo.jpg" alt="Sandy Brook DevWorks Logo" class="hidden h-8 w-8 rounded-full dark:block">
                <div>
                    <span class="text-brand">Sandy Brook</span> ProjectLab
                </div>
            </a>
            <div class="flex gap-8 text-sm text-slate-500">
                <a href="https://sandybrookdevworks.com#services" target="_blank" rel="noopener noreferrer" class="hover:text-brand transition-colors">Services</a>
                <a href="https://sandybrookdevworks.com#about" target="_blank" rel="noopener noreferrer" class="hover:text-brand transition-colors">About</a>
                <a href="https://sandybrookdevworks.com/contact.html" target="_blank" rel="noopener noreferrer" class="hover:text-brand transition-colors">Contact</a>
            </div>
            <div class="text-sm text-slate-500">
                &copy; 2026 Sandy Brook DevWorks LLC. All rights reserved.
            </div>
        </div>
    </div>
</footer>
```

## Guide Content Components

These are available when `guides/content.css` is linked. Wrap guide content in `<main>` for typography styles to apply.

### Callouts

```html
<!-- Default (teal) -->
<div class="callout">
    <strong>Note</strong>
    <p>Default callout text.</p>
</div>

<!-- Tip (green) -->
<div class="callout tip">
    <strong>Tip</strong>
    <p>Helpful suggestion.</p>
</div>

<!-- Warning (amber) -->
<div class="callout warn">
    <strong>Gotcha</strong>
    <p>Something to watch out for.</p>
</div>

<!-- Danger (red) -->
<div class="callout danger">
    <strong>Critical</strong>
    <p>Important warning.</p>
</div>
```

### Code Blocks with Syntax Highlighting

```html
<pre><span class="kw">public</span> <span class="tp">string</span> <span class="fn">GetName</span>()
{
    <span class="kw">return</span> <span class="str">"hello"</span>; <span class="cm">// comment</span>
}</pre>
```

Span classes: `.kw` (keyword/blue), `.tp` (type/teal), `.str` (string/orange), `.fn` (function/yellow), `.cm` (comment/green), `.num` (number/green), `.op` (operator), `.pk` (pink/control flow), `.lp` (loop/blue).

### Tables

```html
<div class="table-wrap">
    <table>
        <thead><tr><th>Column 1</th><th>Column 2</th></tr></thead>
        <tbody><tr><td>Data</td><td>Data</td></tr></tbody>
    </table>
</div>
```

### Challenge Boxes

```html
<div class="challenge">
    <h3>Coding Challenge</h3>
    <p>Challenge description.</p>
</div>
```

### Collapsible Solutions

```html
<details>
    <summary>View Solution</summary>
    <div class="solution-body">
        <pre><!-- solution code --></pre>
    </div>
</details>
```

### Page Navigation (Previous / Next)

```html
<div class="page-nav">
    <a href="previous.html">
        <span class="label">Previous</span>
        <span class="title">Previous Page Title</span>
    </a>
    <a href="next.html" class="next">
        <span class="label">Next</span>
        <span class="title">Next Page Title</span>
    </a>
</div>
```

## How to Add a New Guide

1. Create a directory under `guides/` (e.g., `guides/react/`)
2. Copy any lesson file as a starting template
3. In `<head>`, ensure these links (adjust depth):
   - `<link rel="stylesheet" href="../../styles/brand.css">`
   - `<link rel="stylesheet" href="../content.css">`
   - The inline `<style type="text/tailwindcss">` block (7 lines)
   - The inline dark mode init script (1 line)
   - `<script src="../../styles/theme.js"></script>`
4. Update the nav subtitle and lesson links for your guide
5. Write content inside `<main>` using the components above
6. Add a card linking to your guide in `guides/index.html`

## How to Add a New Top-Level Page

1. Create the HTML file at the project root
2. Copy the `<head>` from `index.html` as a template
3. Use `styles/brand.css` and `styles/theme.js` (no depth prefix needed)
4. Do NOT link `guides/content.css` unless the page has guide-style content
5. Add a nav link if appropriate
