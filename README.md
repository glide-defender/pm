# Defender PM

Project management workspace for ADRM Security's Defender platform. Delivered as a Glide web embed; Make.com handles backend automation.

## Architecture

- **Shell:** `workspace.html` — navigation, shared utilities, postMessage dispatcher
- **Sections:** `section-{key}.html` — 19 individual section files, each self-contained and rendered inside iframes via `srcdoc`
- **Bundle:** `workspace-all.html` — single-file output produced by `bundle.py`, loaded directly by Glide
- **Backend:** Make.com webhooks (`https://hook.us1.make.com/...`) for all write paths

## Sections

`actions`, `schedule`, `punch`, `observations`, `risks`, `rfi`, `raci`, `materials`, `deployment`, `finance`, `contacts`, `meetings`, `time`, `files`, `assets`, `activity`, `audit`, `mywork`, `scorecards`

## Build

Bundle is produced locally:

```bash
python bundle.py
```

This reads `workspace.html` + all `section-*.html` files, escapes section contents for safe embedding in `__SECDOCS__` strings, and writes `workspace-all.html`. Commit the updated bundle after every change.

## Embedding in Glide

Glide pulls the bundle from jsDelivr:

```
https://cdn.jsdelivr.net/gh/glide-defender/pm@main/workspace-all.html
```

jsDelivr caches aggressively. After a push, force-purge with:

```
https://purge.jsdelivr.net/gh/glide-defender/pm@main/workspace-all.html
```

During active development, append `?v={timestamp}` to the Glide embed URL to defeat both jsDelivr and Glide's own cache.

## Docs

- `DEFENDER-HANDOFF.md` — architecture, patterns, progress engine, aesthetic rules, pending work
- `INGESTION-TEMPLATE.md` — payload ingestion pattern applied per-section
- `PAYLOAD-SCHEMA.md` — canonical payload shape
- `POST-INGESTION-PUNCHLIST.md` — follow-up items after ingestion pass
- `AGENT-PHASE-1-SPEC.md` — agent integration spec

## License

Proprietary. All rights reserved, ADRM Security.
