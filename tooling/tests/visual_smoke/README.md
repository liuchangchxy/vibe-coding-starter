# Visual smoke (opt-in, for projects with a web surface)

## What it does

Screenshots every route in a headless browser at two viewports (desktop 1280 and phone 390). Shots are archived for review and never committed.

## Two judging layers

1. **Machine: is it blank?** One or fewer unique colors, or too low an ink ratio → red (runnable in CI).
2. **Human/AI side-by-side review**: put shots next to a reference, a competitor, or the previous version and judge *is it good*. Machines cannot test that layer — see `standards/TESTING.md` §1.8.

## Identity signals ("not blank" must also be "ours")

Judging only "not blank" lets a page full of content that *isn't your app* pass (real precedent: an error placeholder page has content and is not pure white, so a color-only criterion waves it through). So four identity signals must pass before the color criterion, and any miss is red:

1. **Artifact self-check** — the directory under test really is this build's output (entry file + bootstrap script + main script all present). Otherwise refuse immediately;
2. **Main document status** — the main frame only (filtering out iframe sub-documents) responds 2xx/304;
3. **Main script loaded** — the app's main script really loaded once. HTTP 200 alone is not enough; confirm the content is this build;
4. **Host element present** — the page contains the app framework's mount point (e.g. Flutter's `flt-glass-pane`, React's `#root`).

Use a flag (e.g. `--allow-missing-host`) for the escape hatch rather than dismantling the gate: when the framework changes renderer or mount-point naming, one flag moves on and the criteria themselves do not degrade.

## Usage

```bash
# 1. Start the app (any static server or dev server)
# 2. Start headless Chrome (desktop viewport)
"Google Chrome" --headless=new --no-sandbox --window-size=1280,900 \
  --remote-debugging-port=9222 --user-data-dir=/tmp/shotprof about:blank &
# 3. Screenshot (hash-routing example; drop the '#' for non-hash routing)
node shot.mjs http://localhost:9222 http://localhost:8000 ./shots / /settings /trash
# 4. Repeat for the phone viewport (different port + window size + output dir)
```

## Conventions

- The `#` prefix applies only to hash-routed SPAs; adjust `Page.navigate`'s URL construction to your routing.
- `document.readyState` only means "loaded". First-frame stability comes from `--settle` (default 2500ms); raise it for heavy first screens.
- Shots are review archives only. Never commit them (large, and the diff is meaningless).
