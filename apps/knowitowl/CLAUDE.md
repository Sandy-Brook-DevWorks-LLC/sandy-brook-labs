# CLAUDE.md — KnowItOwl! Landing Site

## Project Overview

Static landing site for the KnowItOwl! iOS/watchOS voice Q&A app. Lives as a subpath of the Sandy Brook Projects Lab site (`sandybrook.io/apps/knowitowl/`). Three pages: home (app marketing), privacy policy (legal/compliance), and support (contact form + FAQ).

- **URL:** https://sandybrook.io/apps/knowitowl/
- **Hosting:** GitHub Pages (served from the parent `sandy-brook-labs` repo, which has the `sandybrook.io` CNAME)
- **Parent Repo:** `Sandy-Brook-DevWorks-LLC/sandy-brook-labs` — local path: `~/Repos/sandy-brook-labs`
- **Company:** Sandy Brook DevWorks LLC (Texas)
- **Contact:** hello@sandybrook.io

## Related Repos

- **iOS/watchOS app:** `cloudreyes/gnosisai-iosapp` — local path: `~/Repos/gnosisai-iosapp`
- **Backend:** `cloudreyes/gnosisai-backend` — local path: `~/Repos/gnosisai-backend`

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
    favicon-32x32.png      # 32x32
    favicon-16x16.png      # 16x16
    favicon.ico            # Multi-size ICO (16, 32, 48)
    favicon.svg            # SVG favicon
    site.webmanifest        # PWA manifest (name, icons, theme)
    safari-pinned-tab.svg  # Safari pinned tab icon
    web-app-manifest-*.png # PWA manifest icons (192, 512)
    android-chrome-*.png   # Android home screen icons
```

## Key Content Details

### Credit System (must stay in sync with iOS app)

- **Welcome credits:** 20 credits for new users (one-time)
- **Monthly free credits:** 5 credits per month
- **Credit packs (consumable, never expire):**
  - Standard: 50 credits / $2.99
  - Popular: 100 credits / $4.99
  - Power: 200 credits / $7.99

### Privacy Commitments (reflected in privacy.html)

- **No PII collected** — only Apple's opaque user identifier; no name, email, phone, or location
- User data is **never** sold, rented, or shared with data brokers or aggregators
- User data is **never** used for AI model training
- **Client-side end-to-end encryption** — AES-256-GCM via Apple CryptoKit; Firestore/Storage only store ciphertext
- **User-scoped encryption keys** — stored in iCloud Keychain, never leave user's devices
- Data stored in Firebase (Firestore + Storage) in `nam5` (multi-region US, 99.999% SLA)
- Authentication via Sign in with Apple with cryptographic nonce (Firebase Auth)
- Apple ID credential revocation detection (auto-sign out)
- Credit operations via tamper-proof Cloud Functions (server-side validation)
- Users can delete their conversation data (messages + audio) directly within the app
- Firebase Crashlytics for crash/error reporting only (no PII, no conversation content)
- No behavioral analytics, no tracking, no ads

### Third-Party Services (disclosed in privacy policy)

- **Google Gemini** (via Firebase AI Logic) — processes voice/text queries
- **Firebase** — Auth, Firestore, Storage, App Check, Cloud Functions (credit management), Crashlytics (crash/error reporting)
- **Apple** — Sign in with Apple, In-App Purchases, iCloud KV (settings only)

## Conventions

- All pages are self-contained HTML files using Tailwind CSS CDN with minimal inline CSS (no external stylesheets or scripts beyond Tailwind and Google Fonts)
- Responsive design with mobile-first approach
- Dark/light mode support via Tailwind `dark:` classes (toggled by class, persisted in localStorage)
- Sage green accent color matching the app (`#6B8E7E` primary)
- Scroll-triggered fade-in animations via IntersectionObserver
- Contact form uses Formspree (`https://formspree.io/f/...`)
- FAQ uses native `<details>/<summary>` elements (no JS needed)

## Deployment

Push to `main` in the parent `sandy-brook-labs` repo. GitHub Pages auto-deploys. No build step required.

```bash
git add -A && git commit -m "message" && git push
```

Changes appear at `https://sandybrook.io/apps/knowitowl/` within minutes.

## Known Issues

- **No build step** — All pages use Tailwind CSS CDN with shared config inline in each file. Changes to shared styles (nav, footer, colors, Tailwind config) must be manually replicated across all three files.
- **Formspree contact form** — Requires a Formspree account. The form action URL is hardcoded in `support.html`.
- **App Store link** — Currently uses a placeholder `#` href on the App Store badge. Must be updated with the real App Store URL after approval.
- **Sitemap entries** — Lives in the parent site root at `sandybrook.io/sitemap.xml`. Any new pages added here must also be listed there.

## Changelog

- **2026-03-18:** Updated `privacy.html` section 4 (Google Gemini / AI Processing) to explicitly enumerate data types sent to Google's servers (voice audio recordings, text messages, conversation history up to 10 messages), reference Google Cloud Data Processing Addendum for equivalent protection, and note that the app obtains explicit in-app consent before sending data — addressing App Store rejection Guidelines 5.1.1(i) & 5.1.2(i).
