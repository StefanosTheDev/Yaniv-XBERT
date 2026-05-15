# XBert — Next.js + TypeScript

Next.js 14 (App Router, TS) version of the XBert marketing site. Every route's
UI is the original static HTML rendered verbatim via `dangerouslySetInnerHTML`,
so the design is byte-identical to the original static build. The structure is
set up so individual pages can be progressively refactored into real React
components without disrupting the rest of the site.

## Run

```bash
npm install
npm run dev      # http://localhost:3000
npm run build    # production build
npm start
```

Deploy: push to Git, import on Vercel, no config needed.

## Structure

- `app/layout.tsx` — shared `<head>` (fonts, Remixicon, base/nav/shared/footer CSS) and the Lottie web-component bootstrap.
- `app/<route>/page.tsx` — one server component per route. Injects the page-specific stylesheet, applies the `page-*` class on a wrapper, and renders the body HTML.
- `components/LegacyPage.tsx` — wrapper that does `dangerouslySetInnerHTML` and loads `/script.js` with `strategy="afterInteractive"`.
- `components/legacy/*.html` — the authoritative page body partials. Edit these to change page content.
- `public/styles/`, `public/assets/`, `public/script.js` — static assets served from the site root.

## Notes on the script.js

`public/script.js` has one small mod versus a raw `<script>` at the end of `<body>`: the outer `DOMContentLoaded` listener is wrapped so it also runs when the script is injected *after* the event has already fired (which is what Next's `afterInteractive` strategy does). All page behaviour — mobile nav, reveal-on-scroll, Lottie hookups — is otherwise unchanged.

## Path to real React components

To migrate a page off the legacy HTML shell:

1. Extract `Nav` and `Footer` into `components/` first so all pages can share them.
2. Replace the `<LegacyPage ... />` call in the page's `page.tsx` with real JSX.
3. Move any behavior that was in `public/script.js` and was specific to that page into a client component with `useEffect`.

The other pages keep working while you refactor.

test

