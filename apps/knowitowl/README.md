# KnowItOwl! — Landing Site

Static marketing and support website for the [KnowItOwl!](https://sandybrook.io/apps/knowitowl/) iOS/watchOS voice Q&A app.

## Pages

- **[Home](https://sandybrook.io/apps/knowitowl/)** — App features, screenshots, App Store download link
- **[Privacy Policy](https://sandybrook.io/apps/knowitowl/privacy.html)** — How we handle user data (CCPA/CPRA compliant)
- **[Support](https://sandybrook.io/apps/knowitowl/support.html)** — Contact form and frequently asked questions

## Tech Stack

- Plain HTML, CSS, and JavaScript — no framework, no build step
- Hosted as a subpath of the Sandy Brook Projects Lab site (`sandybrook.io/apps/knowitowl/`) via GitHub Pages
- Responsive design with dark/light mode support
- Google Fonts (Inter)

## Development

Edit HTML files directly. No dependencies to install.

To preview locally from the repo root:

```bash
python3 -m http.server 8080
```

Then open [http://localhost:8080/apps/knowitowl/](http://localhost:8080/apps/knowitowl/).

## Deployment

Push to `main`. GitHub Pages deploys the parent `sandy-brook-labs` repo automatically. Changes are live at [sandybrook.io/apps/knowitowl/](https://sandybrook.io/apps/knowitowl/) within minutes.

## Related Repos

| Repo | Description |
|------|-------------|
| [know-it-owl](https://github.com/Sandy-Brook-DevWorks-LLC/know-it-owl) | Unified iOS/watchOS app, .NET API, Firebase configuration, and Google Cloud infrastructure |

## License

Copyright 2026 Sandy Brook DevWorks LLC. All rights reserved.
