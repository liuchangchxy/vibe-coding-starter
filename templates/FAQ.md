# ❓ FAQ & Troubleshooting

The most common questions, typical errors, and root-cause fixes encountered while installing, developing, deploying, and running this project.

<p align="center"><a href="FAQ.md">English</a> · <a href="FAQ.zh-CN.md">简体中文</a></p>

---

## 🛠️ Part 1 — Setup and environment

### Q1: A `UnicodeDecodeError: 'gbk' codec can't decode...` when running tests locally?
* **Root cause**: on Windows the console encoding is often GBK. A bare `subprocess.run(..., text=True)` or a file read without an explicit encoding will garble UTF-8 content.
* **Fix**:
  1. Pass `encoding="utf-8", errors="replace"` to every `subprocess.run(..., text=True)`;
  2. Always declare `open(..., encoding="utf-8")`;
  3. In Windows PowerShell, set `$OutputEncoding = [Console]::InputEncoding = [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()`.

### Q2: Missing dependencies or incompatible versions?
* **Fix**:
  - Python: use a virtual environment (`python -m venv .venv`), activate it, then `pip install -r requirements.txt`.
  - Node.js: use `pnpm install` or `npm ci` so `package-lock.json` pins versions.
  - Last resort: open the project in the `.devcontainer/` for a clean, air-gapped container.

---

## 🌐 Part 2 — Localization and dark mode

### Q3: After switching to English, dialogs and error messages are still in Chinese?
* **Root cause**: the backend concatenated human-readable sentences (e.g. `raise HTTPException(detail="topic not found")`) and the frontend rendered that hardcoded string directly.
* **Fix**: obey the localization contract — the backend **never returns a natural-language sentence**. Return a structured code plus parameters: `{"error_code": "TOPIC_NOT_FOUND", "params": {"id": 123}}`, and let the presentation layer translate it. See `standards/LOCALIZATION.md`.

### Q4: A white flash or style flicker (FOUC) when switching language or theme?
* **Root cause**: the theme or language preference is applied only after the framework has fully loaded and hydrated.
* **Fix**: inline a zero-dependency script in the entry `<head>` that reads `theme` / `locale` from storage and applies it to the root element before first paint. See the Web adapter in `standards/LOCALIZATION.md`.

---

## 📂 Part 3 — Paths and portability

### Q5: `FileNotFoundError: C:\Users\...` on someone else's machine or on CI?
* **Root cause**: a hardcoded absolute path violated the no-hardcoded-paths rule.
* **Fix**:
  - Python: derive from `Path(__file__).resolve().parent`;
  - Node.js: use `import.meta.url` or `path.resolve(__dirname, ...)`;
  - External and persistent paths come from environment variables, with a safe relative default.

---

## 🧪 Part 4 — Tests and automated gates

### Q6: Why was my local `git commit` rejected?
* **Root cause**: the project armed `.git/hooks/pre-commit`. A failing suite, detected un-localized raw text, or a tampered assertion physically blocks the commit.
* **Fix**:
  1. Run the local suite (`python -m unittest discover -s tooling/tests` or `npm test`) and read the failing cases;
  2. Fix the implementation until it is green. Never bypass with `git commit --no-verify`.

### Q7: The report shows `skipped > 0`. Can we accept delivery?
* **Root cause**: per `standards/TESTING.md`, `skipped` is not passing. Distinguish an *environmental* skip (missing external hardware) from an *assertion* skip (the case never really ran).
* **Fix**: an assertion skip is an absolute veto — the case must actually run. An environmental skip must be declared item by item, with the reason, in the documentation.
