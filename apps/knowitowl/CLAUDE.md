# CLAUDE.md — KnowItOwl! Landing Site

## Project Overview

Static landing site for the KnowItOwl! iOS/watchOS voice Q&A app. Lives as a subpath of the Sandy Brook Projects Lab site (`sandybrook.io/apps/knowitowl/`). Three pages: home (app marketing), privacy policy (legal/compliance), and support (contact form + FAQ).

- **URL:** https://sandybrook.io/apps/knowitowl/
- **Hosting:** GitHub Pages (served from the parent `sandy-brook-labs` repo, which has the `sandybrook.io` CNAME)
- **Parent Repo:** `Sandy-Brook-DevWorks-LLC/sandy-brook-labs` — local path: `~/Repos/sandy-brook-labs`
- **Company:** Sandy Brook DevWorks LLC (Texas)
- **Contact:** hello@sandybrook.io

## Related Repos

- **Unified app and backend:** `Sandy-Brook-DevWorks-LLC/know-it-owl` — local path: `~/Repos/know-it-owl`

## Tech Stack

- **HTML/CSS/JS** — No build step, no framework, no bundler
- **Hosting:** GitHub Pages via the parent `sandy-brook-labs` repo (the root CNAME `sandybrook.io` covers this subpath)
- **SEO:** Open Graph + Twitter Card meta tags, JSON-LD structured data. Sitemap and robots.txt live at the parent site root, not inside this folder.
- **Fonts:** Google Fonts (Inter)
- **Icons:** Favicon set in `favicon/` directory (multiple sizes + `site.webmanifest`)
- **Analytics:** None (privacy-first)

## Pages

| File | URL | Purpose |
|------|-----|---------|
| `index.html` | `sandybrook.io/apps/knowitowl/` | Marketing landing page — app features, screenshots, App Store link |
| `privacy.html` | `sandybrook.io/apps/knowitowl/privacy.html` | Privacy policy — 14 sections, CCPA/CPRA compliant |
| `support.html` | `sandybrook.io/apps/knowitowl/support.html` | Contact form (Formspree) + FAQ sidebar |

## Project Structure

```
apps/knowitowl/
  CLAUDE.md                # This file
  README.md                # Public-facing documentation
  index.html               # Landing page
  privacy.html             # Privacy policy (14 sections)
  support.html             # Support/contact page with FAQ
  favicon/
    apple-touch-icon.png   # 180x180
    favicon-96x96.png      # 96x96
    favicon.ico            # Multi-size ICO (16, 32, 48)
    favicon.svg            # SVG favicon
    site.webmanifest        # PWA manifest (name, icons, theme)
    web-app-manifest-*.png # PWA manifest icons (192, 512)
  styles/
    main.css                # Shared page styling, glass nav, animations, FAQ details, print rules
  scripts/
    tailwind-config.js      # Tailwind CDN sage/cream palette and font stack
    theme-toggle.js         # Dark mode toggle wiring and localStorage persistence
    scroll-fade-in.js       # Landing page section animation observer
    contact-form.js         # Support page Formspree submit handler
```

## Key Content Details

### Credit System (must stay in sync with iOS app)

- **Welcome credits:** 20 credits for new users (one-time)
- **Monthly free credits:** 5 credits per month
- **Credit packs (consumable, never expire):**
  - Standard: 30 credits
  - Popular: 60 credits
  - Power: 120 credits
- Localized App Store prices shown in the app are authoritative.

### Privacy Commitments (reflected in privacy.html)

- **No sign-in screen and no name/email account** — the backend derives an opaque identifier from Apple's signed, app-scoped App Transaction
- User data is **never** sold, rented, or shared with data brokers or aggregators
- User data is **never** used for AI model training
- **Client-side encrypted storage** — saved conversation history and audio use AES-256-GCM via Apple CryptoKit; Firestore/Storage only store ciphertext
- **User-scoped encryption keys** — stored in synchronizable Keychain for cross-device history
- Data stored in Firebase (Firestore + Storage) in `nam5` (multi-region US, 99.999% SLA)
- The backend validates Apple's App Transaction and mints a Firebase custom-token session
- Credit operations use the authenticated Cloud Run API and server-side validation
- Users can withdraw AI-processing consent, which stops new iPhone and Watch questions until consent is restored
- Delete Personal Data erases conversations, stored audio, profile data, encryption key, consent, and the active Firebase Auth user/session
- Credit balance, credit ledger, and redeemed StoreKit transaction claims remain after deletion to preserve purchases and prevent duplicate grants
- Native Apple crash reports plus privacy-filtered backend diagnostics replace third-party crash reporting
- No behavioral analytics, no tracking, no ads

### Third-Party Services (disclosed in privacy policy)

- **KnowItOwl! AI API** — authenticated bridge operated by Sandy Brook DevWorks for transcription, answer generation, and text-to-speech
- **Google Cloud Speech-to-Text, Vertex AI Gemini, Google Search grounding, and Cloud Text-to-Speech** — process voice/text questions and generate answers through the KnowItOwl! API
- **Firebase** — Auth, Firestore, Storage, and App Check
- **Apple** — app-scoped App Transaction identity, In-App Purchases, synchronizable Keychain, iCloud KV, and native crash reporting

## Conventions

- All pages use Tailwind CSS CDN plus shared app-local files under `styles/` and `scripts/`.
- Keep the dark-mode init snippet inline in each page's `<head>` so the `dark` class is applied before paint.
- Tailwind palette/config lives in `scripts/tailwind-config.js`; page styling belongs in `styles/main.css`.
- Responsive design with mobile-first approach
- Dark/light mode support via Tailwind `dark:` classes (toggled by class, persisted in localStorage)
- Sage green accent color matching the app (`#6B8E7E` primary)
- Scroll-triggered fade-in animations via IntersectionObserver
- Contact form uses Formspree (`https://formspree.io/f/...`)
- FAQ uses native `<details>/<summary>` elements (no JS needed)
- App Store links currently point to `https://apps.apple.com/us/app/knowitowl-q-a-on-your-wrist/id6759131642`.

## Deployment

Push to `main` in the parent `sandy-brook-labs` repo. GitHub Pages auto-deploys. No build step required.

```bash
git add -A && git commit -m "message" && git push
```

Changes appear at `https://sandybrook.io/apps/knowitowl/` within minutes.

## Known Issues

- **No build step** — Tailwind is loaded from the CDN. Shared app behavior lives in `styles/main.css` and `scripts/*.js`.
- **Formspree contact form** — Requires a Formspree account. The form action URL is hardcoded in `support.html`.
- **Sitemap entries** — Lives in the parent site root at `sandybrook.io/sitemap.xml`. Any new pages added here must also be listed there.

## Changelog

- **2026-09-05:** Updated product, privacy, support, and repository documentation for KnowItOwl! 4.0: account-free App Transaction identity, consent withdrawal, personal-data deletion with commerce-record retention, current credit packs, Cloud Run processing, and native Apple crash reports.
- **2026-07-03:** Updated `privacy.html` and `support.html` to reflect the current AI API architecture: device requests go through the authenticated KnowItOwl! AI API before Google Vertex AI/Gemini and Google Cloud Text-to-Speech, saved Firebase history/audio remains client-side encrypted, and context is limited to up to 3 recent messages.
- **2026-03-18:** Updated `privacy.html` section 4 (Google Gemini / AI Processing) to explicitly enumerate data types sent to Google's servers (voice audio recordings, text messages, conversation history up to 10 messages), reference Google Cloud Data Processing Addendum for equivalent protection, and note that the app obtains explicit in-app consent before sending data — addressing App Store rejection Guidelines 5.1.1(i) & 5.1.2(i).
