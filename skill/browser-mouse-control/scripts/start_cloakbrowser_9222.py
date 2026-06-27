from __future__ import annotations

import signal
import sys
import time
from pathlib import Path

import cloakbrowser


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    log_hint = root / "logs"
    log_hint.mkdir(exist_ok=True)
    browser = cloakbrowser.launch(
        headless=False,
        humanize=True,
        args=[
            "--remote-debugging-port=9222",
            "--no-first-run",
            "--no-default-browser-check",
        ],
    )
    print("CloakBrowser running on http://127.0.0.1:9222", flush=True)

    stopped = False

    def stop(_signum, _frame):
        nonlocal stopped
        stopped = True

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)

    try:
        while not stopped:
            time.sleep(1)
    finally:
        browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
