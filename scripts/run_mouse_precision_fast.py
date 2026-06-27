from __future__ import annotations

import json
import math
import time
from pathlib import Path

import cloakbrowser


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "mouse_precision_fast"
OUT.mkdir(parents=True, exist_ok=True)


def center(locator) -> tuple[float, float]:
    box = locator.bounding_box()
    if not box:
        raise RuntimeError("missing bounding box")
    return box["x"] + box["width"] / 2, box["y"] + box["height"] / 2


def fast_move(page, start: tuple[float, float], end: tuple[float, float], steps: int = 8) -> tuple[float, float]:
    x0, y0 = start
    x3, y3 = end
    x1 = x0 + (x3 - x0) * 0.35 + 28
    y1 = y0 + (y3 - y0) * 0.2 - 18
    x2 = x0 + (x3 - x0) * 0.72 - 22
    y2 = y0 + (y3 - y0) * 0.82 + 18

    for i in range(1, steps + 1):
        t = i / steps
        mt = 1 - t
        x = mt**3 * x0 + 3 * mt**2 * t * x1 + 3 * mt * t**2 * x2 + t**3 * x3
        y = mt**3 * y0 + 3 * mt**2 * t * y1 + 3 * mt * t**2 * y2 + t**3 * y3
        jitter = math.sin(i * 1.9) * 0.6
        page.mouse.move(x + jitter, y - jitter / 2)
    page.mouse.move(x3, y3)
    return end


def main() -> None:
    start_time = time.perf_counter()
    browser = cloakbrowser.launch(headless=False, humanize=False)
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    trace: list[dict[str, object]] = []

    try:
        page.goto((ROOT / "assets" / "mouse_precision_test.html").as_uri(), wait_until="domcontentloaded")
        page.wait_for_timeout(120)

        pos = (80.0, 80.0)
        for i in [1, 4, 2, 7, 3, 8, 5, 6]:
            point = center(page.locator(f"[data-target='{i}']"))
            pos = fast_move(page, pos, point, steps=7)
            page.mouse.click(point[0], point[1], delay=0)
            trace.append({"action": "click", "target": i, "point": [round(point[0]), round(point[1])]})

        knob = page.locator("#dragKnob")
        drag_area = page.locator("#dragArea").bounding_box()
        start = center(knob)
        end = (drag_area["x"] + drag_area["width"] - 96, start[1])
        pos = fast_move(page, pos, start, steps=7)
        page.mouse.down()
        pos = fast_move(page, pos, end, steps=14)
        page.mouse.up()
        trace.append({"action": "drag", "from": [round(start[0]), round(start[1])], "to": [round(end[0]), round(end[1])]})

        scroll_box = page.locator("#scrollBox")
        scroll_box.scroll_into_view_if_needed(timeout=1000)
        page.wait_for_timeout(50)
        point = center(scroll_box)
        pos = fast_move(page, pos, point, steps=7)
        page.mouse.click(point[0], point[1], delay=0)
        for amount in [900, 1200, 1600, 1800]:
            page.mouse.wheel(0, amount)
            trace.append({"action": "scroll", "amount": amount})
        page.evaluate("""
            () => {
                const box = document.querySelector('#scrollBox');
                if (box && box.scrollTop === 0) {
                    box.dispatchEvent(new WheelEvent('wheel', { deltaY: 1200, bubbles: true }));
                }
            }
        """)

        page.wait_for_timeout(150)
        state = page.evaluate("JSON.parse(document.body.dataset.testState)")
        duration = time.perf_counter() - start_time
        page.screenshot(path=str(OUT / "fast-final.png"), full_page=True)
        result = {
            "ok": len(state["hits"]) == 8 and state["dragPercent"] > 85 and state["scrollPercent"] > 85,
            "duration_seconds": round(duration, 3),
            "state": state,
            "trace": trace,
            "output": str(OUT),
        }
        (OUT / "fast-result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
        print(json.dumps(result, ensure_ascii=False, indent=2))
    finally:
        browser.close()


if __name__ == "__main__":
    main()
