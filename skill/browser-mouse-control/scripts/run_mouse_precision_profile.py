from __future__ import annotations

import argparse
import json
import math
import time
from dataclasses import dataclass
from pathlib import Path

import cloakbrowser


ROOT = Path(__file__).resolve().parents[1]
OUT_ROOT = ROOT / "output" / "mouse_precision_profiles"


@dataclass(frozen=True)
class SpeedProfile:
    name: str
    description: str
    headless: bool
    humanize: bool
    move_steps: int
    move_pause: float
    click_delay_ms: int
    post_click_wait_ms: int
    screenshot_each_phase: bool
    dom_check_retries: int
    retry_failed_phase: bool


PROFILES = {
    "fast": SpeedProfile(
        name="fast",
        description="极速档：适合后台系统、自己的网站、本地页面、稳定工具页。",
        headless=False,
        humanize=False,
        move_steps=7,
        move_pause=0.0,
        click_delay_ms=0,
        post_click_wait_ms=0,
        screenshot_each_phase=False,
        dom_check_retries=1,
        retry_failed_phase=False,
    ),
    "natural": SpeedProfile(
        name="natural",
        description="自然档：适合普通网站采集，鼠标移动、停顿、滚动更像真人。",
        headless=False,
        humanize=True,
        move_steps=28,
        move_pause=0.006,
        click_delay_ms=45,
        post_click_wait_ms=120,
        screenshot_each_phase=True,
        dom_check_retries=2,
        retry_failed_phase=True,
    ),
    "careful": SpeedProfile(
        name="careful",
        description="谨慎档：适合结构复杂、风控强、容易变的站点，保留截图、DOM 检查、失败重试和断点信息。",
        headless=False,
        humanize=True,
        move_steps=54,
        move_pause=0.014,
        click_delay_ms=95,
        post_click_wait_ms=280,
        screenshot_each_phase=True,
        dom_check_retries=4,
        retry_failed_phase=True,
    ),
}


def center(locator) -> tuple[float, float]:
    box = locator.bounding_box()
    if not box:
        raise RuntimeError("missing bounding box")
    return box["x"] + box["width"] / 2, box["y"] + box["height"] / 2


def profile_move(
    page,
    start: tuple[float, float],
    end: tuple[float, float],
    profile: SpeedProfile,
) -> tuple[float, float]:
    x0, y0 = start
    x3, y3 = end
    x1 = x0 + (x3 - x0) * 0.32 + 44
    y1 = y0 + (y3 - y0) * 0.18 - 28
    x2 = x0 + (x3 - x0) * 0.74 - 36
    y2 = y0 + (y3 - y0) * 0.82 + 30

    for i in range(1, profile.move_steps + 1):
        t = i / profile.move_steps
        mt = 1 - t
        x = mt**3 * x0 + 3 * mt**2 * t * x1 + 3 * mt * t**2 * x2 + t**3 * x3
        y = mt**3 * y0 + 3 * mt**2 * t * y1 + 3 * mt * t**2 * y2 + t**3 * y3
        jitter = math.sin(i * 1.73) * (0.35 if profile.name == "fast" else 1.05)
        page.mouse.move(x + jitter, y - jitter / 2)
        if profile.move_pause:
            time.sleep(profile.move_pause + (i % 4) * profile.move_pause * 0.25)
    page.mouse.move(x3, y3)
    return end


def screenshot(page, out_dir: Path, name: str, enabled: bool, full_page: bool = False) -> str | None:
    if not enabled:
        return None
    path = out_dir / name
    page.screenshot(path=str(path), full_page=full_page)
    return str(path)


def wait_state(page, predicate: str, retries: int, wait_ms: int) -> bool:
    for _ in range(max(1, retries)):
        if page.evaluate(predicate):
            return True
        page.wait_for_timeout(wait_ms)
    return bool(page.evaluate(predicate))


def run(profile: SpeedProfile) -> dict[str, object]:
    out_dir = OUT_ROOT / profile.name
    out_dir.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    trace: list[dict[str, object]] = []
    screenshots: list[str] = []

    browser = cloakbrowser.launch(headless=profile.headless, humanize=profile.humanize)
    page = browser.new_page(viewport={"width": 1280, "height": 900})

    try:
        page.goto((ROOT / "assets" / "mouse_precision_test.html").as_uri(), wait_until="domcontentloaded")
        page.wait_for_timeout(120 if profile.name == "fast" else 600)
        first = screenshot(page, out_dir, "01-ready.png", profile.screenshot_each_phase, full_page=True)
        if first:
            screenshots.append(first)

        pos = (80.0, 80.0)
        click_order = [1, 4, 2, 7, 3, 8, 5, 6]
        for target_id in click_order:
            point = center(page.locator(f"[data-target='{target_id}']"))
            pos = profile_move(page, pos, point, profile)
            page.mouse.click(point[0], point[1], delay=profile.click_delay_ms)
            if profile.post_click_wait_ms:
                page.wait_for_timeout(profile.post_click_wait_ms)
            ok = wait_state(
                page,
                f"() => JSON.parse(document.body.dataset.testState).hits.includes('{target_id}')",
                profile.dom_check_retries,
                120,
            )
            if not ok and profile.retry_failed_phase:
                pos = profile_move(page, pos, point, profile)
                page.mouse.click(point[0], point[1], delay=profile.click_delay_ms)
                ok = wait_state(
                    page,
                    f"() => JSON.parse(document.body.dataset.testState).hits.includes('{target_id}')",
                    profile.dom_check_retries,
                    160,
                )
            trace.append(
                {
                    "action": "click",
                    "target": target_id,
                    "point": [round(point[0]), round(point[1])],
                    "ok": ok,
                }
            )

        shot = screenshot(page, out_dir, "02-clicks.png", profile.screenshot_each_phase, full_page=True)
        if shot:
            screenshots.append(shot)

        knob = page.locator("#dragKnob")
        drag_area = page.locator("#dragArea").bounding_box()
        start = center(knob)
        end = (drag_area["x"] + drag_area["width"] - 96, start[1])
        pos = profile_move(page, pos, start, profile)
        page.mouse.down()
        pos = profile_move(page, pos, end, profile)
        page.mouse.up()
        drag_ok = wait_state(
            page,
            "() => JSON.parse(document.body.dataset.testState).dragPercent >= 85",
            profile.dom_check_retries,
            160,
        )
        trace.append(
            {
                "action": "drag",
                "from": [round(start[0]), round(start[1])],
                "to": [round(end[0]), round(end[1])],
                "ok": drag_ok,
            }
        )

        page.locator("#scrollBox").scroll_into_view_if_needed(timeout=1000)
        page.wait_for_timeout(50 if profile.name == "fast" else 260)
        scroll_box = page.locator("#scrollBox")
        point = center(scroll_box)
        pos = profile_move(page, pos, point, profile)
        page.mouse.click(point[0], point[1], delay=profile.click_delay_ms)
        for amount in [900, 1200, 1600, 1800]:
            page.mouse.wheel(0, amount)
            if profile.post_click_wait_ms:
                page.wait_for_timeout(min(profile.post_click_wait_ms, 180))
            trace.append({"action": "scroll", "amount": amount})

        scroll_ok = wait_state(
            page,
            "() => JSON.parse(document.body.dataset.testState).scrollPercent >= 85",
            profile.dom_check_retries,
            180,
        )
        if not scroll_ok and profile.retry_failed_phase:
            page.locator("#scrollBox").evaluate("(el) => el.scrollTop = el.scrollHeight")
            scroll_ok = wait_state(
                page,
                "() => JSON.parse(document.body.dataset.testState).scrollPercent >= 85",
                profile.dom_check_retries,
                180,
            )
            trace.append({"action": "scroll-retry", "method": "container-scrollTop", "ok": scroll_ok})

        final_shot = screenshot(page, out_dir, "99-final.png", True, full_page=True)
        screenshots.append(final_shot)
        state = page.evaluate("JSON.parse(document.body.dataset.testState)")
        duration = time.perf_counter() - started
        result = {
            "ok": len(state["hits"]) == 8 and state["dragPercent"] >= 85 and state["scrollPercent"] >= 85,
            "profile": profile.name,
            "description": profile.description,
            "duration_seconds": round(duration, 3),
            "state": state,
            "trace": trace,
            "screenshots": screenshots,
            "output": str(out_dir),
        }
        (out_dir / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
        return result
    finally:
        browser.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run CloakBrowser mouse precision test with speed profiles.")
    parser.add_argument("--profile", choices=sorted(PROFILES), default="natural")
    parser.add_argument("--list-profiles", action="store_true")
    args = parser.parse_args()

    if args.list_profiles:
        print(json.dumps({name: profile.description for name, profile in PROFILES.items()}, ensure_ascii=False, indent=2))
        return

    print(json.dumps(run(PROFILES[args.profile]), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
