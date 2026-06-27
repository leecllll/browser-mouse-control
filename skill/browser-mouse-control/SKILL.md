---
name: browser-mouse-control
description: Use when Codex needs precise browser-side mouse control for authorized web workflows through CloakBrowser or a CDP-enabled Chrome browser with Playwright, including mouse movement, clicks, drag, scroll, screenshots, DOM/network verification, tiny-loop crawler prototyping, and reliable script scaling with fast, natural, or careful speed profiles.
---

# Browser Mouse Control（鼠标控制）

This skill helps Codex run flexible browser automation with precise browser-side mouse control through CloakBrowser plus Playwright/CDP. Use it when the user wants high-precision browser mouse movement, crawler prototyping, screenshot-based inspection, DOM validation, or a repeatable workflow for complex web tasks.

The goal is not just "click a page". The goal is:

1. Plan the web flow.
2. Observe the page by screenshot and DOM.
3. Test one tiny end-to-end loop.
4. Correct selectors, waits, scrolling, and mouse paths.
5. Run the full task with logs, screenshots, retries, and handoff files.

Do not use this skill to bypass login, CAPTCHA, access controls, paywalls, or site rules. If authorization is required, ask the user to complete it manually in the browser, then continue from the authorized browser state.

## When To Use

- The user asks for CloakBrowser, Playwright, CDP, stealth browser control, or browser mouse automation.
- The task is an authorized crawler, internal web task, admin panel task, local page test, or stable tool workflow.
- The page depends on hover, mouse movement, drag, wheel scrolling, lazy loading, or human-paced interaction.
- The user wants to compare fast/natural/careful automation speed.
- The user wants a script that can observe, test, retry, and then scale.

## What This Skill Can Do

- Launch CloakBrowser through Python.
- Connect to an existing Chrome DevTools Protocol endpoint such as `http://127.0.0.1:9222`.
- Move, click, drag, scroll, and hover inside the browser viewport.
- Save screenshots after important phases.
- Inspect DOM state, URL, text, list counts, and network results.
- Build a tiny proof script before the full crawler.
- Produce logs, output JSON, screenshots, and resume hints.
- Choose between three speed profiles.

## Installation

From a repo containing this skill and its scripts:

### macOS / Linux

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cloakbrowser install
```

### Windows PowerShell

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cloakbrowser install
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then reopen PowerShell, activate the virtual environment again, and verify:

```powershell
python scripts\run_mouse_precision_profile.py --list-profiles
```

## Installing The Skill Into Codex

Copy the folder `skill/browser-mouse-control` into the user's Codex skills directory.

macOS example:

```bash
mkdir -p ~/.codex/skills
cp -R skill/browser-mouse-control ~/.codex/skills/
```

Windows PowerShell example when `CODEX_HOME` is set:

```powershell
New-Item -ItemType Directory -Force "$env:CODEX_HOME\skills"
Copy-Item -Recurse ".\skill\browser-mouse-control" "$env:CODEX_HOME\skills\"
```

After copying, restart the Codex session so the skill list reloads.

## Speed Profiles

### fast

Use for backend systems, owned sites, local pages, and stable tools.

Behavior:

- Minimal mouse steps.
- Almost no pauses.
- Minimal screenshots.
- DOM check after critical actions.
- Best when the workflow is already known.

Command:

```bash
python scripts/run_mouse_precision_profile.py --profile fast
```

### natural

Use as the default for ordinary web collection.

Behavior:

- Curved mouse paths.
- Short human-like pauses.
- Screenshots after phases.
- DOM checks after clicks, drags, scrolls, and navigation.
- Retry obvious transient failures.

Command:

```bash
python scripts/run_mouse_precision_profile.py --profile natural
```

### careful

Use for complex, changing, or risk-sensitive flows where reliability matters more than raw speed.

Behavior:

- Slower mouse paths.
- More DOM checks.
- More screenshots.
- Retries after failed phases.
- Preserve enough state to diagnose or resume.

Command:

```bash
python scripts/run_mouse_precision_profile.py --profile careful
```

## CDP Connection

If CloakBrowser is already running on a debugging port:

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    context = browser.contexts[0] if browser.contexts else browser.new_context()
    page = context.new_page()
```

To start a CloakBrowser instance on port 9222:

```bash
python scripts/start_cloakbrowser_9222.py
```

Keep that process running in a visible terminal. Verify it from another terminal:

```bash
curl http://127.0.0.1:9222/json/version
```

Windows PowerShell:

```powershell
Invoke-RestMethod http://127.0.0.1:9222/json/version
```

If no CDP endpoint is needed, launch through CloakBrowser directly:

```python
import cloakbrowser

browser = cloakbrowser.launch(headless=False, humanize=True)
page = browser.new_page()
```

## Mouse Precision Test

Use this when the user asks to test control sensitivity or accuracy:

```bash
python scripts/run_mouse_precision_profile.py --profile fast
python scripts/run_mouse_precision_profile.py --profile natural
python scripts/run_mouse_precision_profile.py --profile careful
```

Expected pass criteria:

- 8 click targets hit.
- Drag reaches at least 85%.
- Scroll reaches at least 85%.
- Final screenshot and `result.json` saved under `output/mouse_precision_profiles/<profile>/`.

## Real Task Workflow

For crawler-like work:

1. Plan the browser route and output format.
2. Open the target in CloakBrowser or connect to CDP.
3. Capture a screenshot and inspect the DOM.
4. Identify stable selectors, buttons, list containers, pagination, detail links, and lazy-load triggers.
5. Run a tiny loop: search once, click once, extract one item, save one result.
6. Fix selectors, waits, mouse paths, scroll targeting, and retry points.
7. Run a small batch.
8. Run the full job.
9. Save outputs and summarize paths for the user.

Read `references/workflow.md` for detailed practices.
