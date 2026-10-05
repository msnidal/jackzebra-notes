# Jackzebra Notes

A public listening companion at https://jackzebranotes.com: original lyrics, independent English translations, and sourced phrase notes for all 55 songs on **Zhuang Zhuang Mixtape**. The name and album structure leave room for later releases.

## Build and preview

```sh
python3 scripts/build-pages.py
python3 scripts/serve.py --port 4173
```

Open `http://127.0.0.1:4173/`. Use `?manual` on a song URL to test the hosted reading experience. The optional local preview recognizes recordings from an adjacent `.local-media/manifest.json`; recordings are never in this repository or deployment.

## Editing

- `dist/album.json`: lyrics, translations, note bodies, citations, approximate timing, and credits.
- `src/song.html`: song-page shell.
- `scripts/build-pages.py`: generates home/album pages and complete HTML for every song, plus canonical metadata, structured data, sitemap, robots.txt, and 404 page.
- `dist/app.js`, `style.css`, `timing.mjs`, `routes.mjs`: enhanced listening experience.
- `dist/catalog.css` and `catalog.js`: album directory and legacy fragment-link handling.

Edit the template rather than generated HTML. Run the builder after edits. Song links are real `/zhuang-zhuang/song-name/` URLs. Normal in-page navigation uses History API to preserve connected audio; modifier-clicks still open normal links. Old `#track=55` links on the new domain resolve to the new song route. The earlier private prototype remains separate.

The artist's current official mixtape listing uses English titles. The generator supports an optional verified `originalTitle` rather than inventing Chinese release titles. Chinese lyric text is present in the static pages and discoverable directly.

Phrase bubbles show only the explanation and expandable Sources. The phrase remains highlighted in the lyrics. The data retains editorial note headings for archival purposes; they are not displayed in bubbles or used as new generated headings. Without JavaScript, the complete bilingual lyrics and expandable notes remain readable, with crawlable song links. Audio connection and playback require JavaScript.

## Publication

Push to `main` on `msnidal/jackzebra-notes`. `.github/workflows/pages.yml` builds, validates, uploads only `dist`, and deploys GitHub Pages. No paid runtime, model calls, accounts, recordings, or server backend are required. GitHub Pages settings must use GitHub Actions and the custom domain `jackzebranotes.com`. The `CNAME` file is also included for portability; Actions deployments use the domain configured in repository settings.

Namecheap apex records point to GitHub Pages (`185.199.108.153`, `.109.153`, `.110.153`, `.111.153`); `www` points to `msnidal.github.io`. Keep email records unchanged. Enable Enforce HTTPS after GitHub issues the certificate. Google Search Console has a verified domain property for `jackzebranotes.com`; `https://jackzebranotes.com/sitemap.xml` has been submitted. The initial fetch ran before HTTPS was ready, so confirm a successful fetch after certificate issuance. GitHub’s HTTPS certificate was still queued at launch. Once issued, enable Enforce HTTPS in Settings → Pages (or use `gh api -X PUT repos/msnidal/jackzebra-notes/pages -F https_enforced=true`).

## Checks

```sh
node --check dist/app.js
node scripts/test-timing.mjs
python3 scripts/validate.py
python3 scripts/test-pages.py
```

Checks cover all 55 static routes, complete bilingual lyrics and note bodies, unique titles/canonicals, internal links, sitemap, exact phrase anchors, time ordering, and absence of audio. Browser checks cover desktop/mobile notes, Back navigation, clean route loads, track selection, and retained local playback.

## Content provenance

3,360 display rows (3,341 lyric rows and 19 section labels), 403 phrase notes. Original words come from community sources listed per song; translations are AI-assisted. The 3,178 approximate timed lines include 3,113 AI-aligned onsets and 65 community onsets. 163 unresolved lyric rows intentionally have no timestamp. Timing used local Whisper large-v3 and large-v3-turbo passes; structural checks do not constitute independent listening verification. Lyrics and translations are not artist-authorized. All rights to the music and artwork remain with their respective holders.

Purchased Bandcamp ZIP/FLAC/MP3/M4A/WAV/OGG files are read locally by the browser. They are not uploaded, stored by GitHub, or retained after a reload.
