from __future__ import annotations

import json
import math
import time
from pathlib import Path

import cloakbrowser


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "mouse_precision"
OUT.mkdir(parents=True, exist_ok=True)


def center(locator) -> tuple[float, float]:
    box = locator.bounding_box()
    if not box:
        raise RuntimeError("missing bounding box")
    return box["x"] + box["width"] / 2, box["y"] + box["height"] / 2


def natural_move(page, start: tuple[float, float], end: tuple[float, float], steps: int = 42, pause: float = 0.014) -> tuple[float, float]:
    x0, y0 = start
    x3, y3 = end
    x1 = x0 + (x3 - x0) * 0.28 + 64
    y1 = y0 + (y3 - y0) * 0.18 - 38
    x2 = x0 + (x3 - x0) * 0.76 - 52
    y2 = y0 + (y3 - y0) * 0.82 + 42

    for i in range(1, steps + 1):
        t = i / steps
        mt = 1 - t
        x = mt**3 * x0 + 3 * mt**2 * t * x1 + 3 * mt * t**2 * x2 + t**3 * x3
        y = mt**3 * y0 + 3 * mt**2 * t * y1 + 3 * mt * t**2 * y2 + t**3 * y3
        jitter = math.sin(i * 1.618) * 1.25
        page.mouse.move(x + jitter, y - jitter / 2)
        time.sleep(pause + (i % 4) * 0.002)
    page.mouse.move(x3, y3)
    return end


def main() -> None:
    browser = cloakbrowser.launch(headless=False, humanize=True)
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    trace: list[dict[str, object]] = []

    try:
        page.goto((ROOT / "assets" / "mouse_precision_test.html").as_uri(), wait_until="domcontentloaded")
        page.wait_for_timeout(900)
        page.screenshot(path=str(OUT / "01-ready.png"), full_page=True)

        pos = (80.0, 80.0)
        for i in [1, 4, 2, 7, 3, 8, 5, 6]:
            target = page.locator(f"[data-target='{i}']")
            point = center(target)
            pos = natural_move(page, pos, point, steps=46, pause=0.016)
            page.wait_for_timeout(120)
            page.mouse.down()
            page.wait_for_timeout(80)
            page.mouse.up()
            trace.append({"action": "click", "target": i, "point": [round(point[0]), round(point[1])]})
            page.wait_for_timeout(220)

        page.screenshot(path=str(OUT / "02-clicks-complete.png"), full_page=True)

        knob = page.locator("#dragKnob")
        drag_area = page.locator("#dragArea").bounding_box()
        start = center(knob)
        end = (drag_area["x"] + drag_area["width"] - 96, start[1])
        pos = natural_move(page, pos, start, steps=34, pause=0.014)
        page.mouse.down()
        page.wait_for_timeout(120)
        pos = natural_move(page, pos, end, steps=58, pause=0.015)
        page.mouse.up()
        trace.append({"action": "drag", "from": [round(start[0]), round(start[1])], "to": [round(end[0]), round(end[1])]})
        page.wait_for_timeout(450)

        scroll_box = page.locator("#scrollBox")
        point = center(scroll_box)
        pos = natural_move(page, pos, point, steps=38, pause=0.014)
        for amount in [220, 260, 320, 380, 420]:
            page.mouse.wheel(0, amount)
            trace.append({"action": "scroll", "amount": amount})
            page.wait_for_timeout(260)

        page.screenshot(path=str(OUT / "03-final.png"), full_page=True)
        state = page.evaluate("JSON.parse(document.body.dataset.testState)")
        (OUT / "mouse_trace.json").write_text(json.dumps({"state": state, "trace": trace}, ensure_ascii=False, indent=2))
        print(json.dumps({"ok": True, "state": state, "trace": trace, "output": str(OUT)}, ensure_ascii=False, indent=2))
    finally:
        browser.close()


if __name__ == "__main__":
    main()
