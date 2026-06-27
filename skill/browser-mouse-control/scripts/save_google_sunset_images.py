from __future__ import annotations

import base64
import argparse
import json
import os
import re
import time
from pathlib import Path
from urllib.request import Request, urlopen

import cloakbrowser


ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "output" / "cloakbrowser"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def default_output_dir() -> Path:
    override = os.environ.get("CLOAK_OUTPUT_DIR")
    if override:
        return Path(override).expanduser()

    candidates = [
        Path.home() / "Desktop",
        Path.home() / "OneDrive" / "Desktop",
        Path.home() / "OneDrive - Personal" / "Desktop",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return Path.cwd()


def image_bytes(src: str) -> tuple[bytes, str]:
    if src.startswith("data:"):
        match = re.match(r"^data:([^;,]+)(;base64)?,(.*)$", src)
        if not match:
            raise ValueError("unsupported data URL")
        mime, is_base64, payload = match.groups()
        data = base64.b64decode(payload) if is_base64 else payload.encode()
        return data, mime

    req = Request(
        src,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/145 Safari/537.36",
            "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
            "Referer": "https://www.google.com/",
        },
    )
    with urlopen(req, timeout=20) as response:
        return response.read(), response.headers.get("content-type", "")


def ext_for(mime: str, src: str) -> str:
    mime = mime.lower()
    if "png" in mime:
        return "png"
    if "webp" in mime:
        return "webp"
    if "gif" in mime:
        return "gif"
    if "jpeg" in mime or "jpg" in mime:
        return "jpg"
    match = re.search(r"\.([a-zA-Z0-9]{3,4})(?:[?#]|$)", src)
    return match.group(1).lower() if match else "jpg"


def main() -> None:
    parser = argparse.ArgumentParser(description="Save three visible sunset images from Google Images through CloakBrowser.")
    parser.add_argument("--output-dir", default=None, help="Directory for saved images. Defaults to the desktop when available.")
    args = parser.parse_args()

    out_dir = Path(args.output_dir).expanduser() if args.output_dir else default_output_dir()
    out_dir.mkdir(parents=True, exist_ok=True)

    browser = cloakbrowser.launch(headless=True, humanize=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    saved: list[dict[str, object]] = []
    seen: set[str] = set()

    try:
        page.goto("https://www.google.com/search?tbm=isch&q=%E6%97%A5%E8%90%BD+sunset+photo", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2500)

        # Accept consent dialogs if this profile sees one.
        for text in ["全部接受", "同意", "Accept all", "I agree"]:
            try:
                page.get_by_text(text, exact=False).first.click(timeout=900)
                page.wait_for_timeout(1000)
                break
            except Exception:
                pass

        page.screenshot(path=str(LOG_DIR / "google-sunset-results.png"), full_page=False)

        for round_index in range(4):
            candidates = page.evaluate(
                """() => {
                    const seen = new Set();
                    return [...document.images]
                      .map((img, index) => {
                        const rect = img.getBoundingClientRect();
                        return {
                          index,
                          src: img.currentSrc || img.src || "",
                          alt: img.alt || "",
                          width: img.naturalWidth || img.width || 0,
                          height: img.naturalHeight || img.height || 0,
                          x: rect.x,
                          y: rect.y,
                          w: rect.width,
                          h: rect.height,
                          area: rect.width * rect.height,
                          visible: rect.bottom > 80 && rect.top < innerHeight && rect.right > 0 && rect.left < innerWidth
                        };
                      })
                      .filter(item => item.visible && item.src && item.width >= 90 && item.height >= 70 && item.area >= 5000)
                      .filter(item => !/logo|favicon/.test(item.src))
                      .filter(item => {
                        if (seen.has(item.src)) return false;
                        seen.add(item.src);
                        return true;
                      })
                      .sort((a, b) => b.area - a.area)
                      .slice(0, 30);
                }"""
            )

            for candidate in candidates:
                src = candidate["src"]
                if src in seen:
                    continue
                seen.add(src)
                try:
                    data, mime = image_bytes(src)
                    if len(data) < 5_000:
                        continue
                    ext = ext_for(mime, src)
                    path = out_dir / f"sunset-google-{len(saved) + 1:02d}.{ext}"
                    path.write_bytes(data)
                    saved.append(
                        {
                            "path": str(path),
                            "bytes": len(data),
                            "source": src[:300],
                            "natural_width": candidate["width"],
                            "natural_height": candidate["height"],
                        }
                    )
                    if len(saved) >= 3:
                        break
                except Exception as exc:
                    saved.append({"error": str(exc), "source": str(src)[:160]})
                    saved[:] = [item for item in saved if "path" in item]

            if len(saved) >= 3:
                break
            page.mouse.wheel(0, 900)
            page.wait_for_timeout(1200 + round_index * 300)

        (LOG_DIR / "google-sunset-saved.json").write_text(json.dumps(saved, ensure_ascii=False, indent=2))

        if len(saved) < 3:
            raise RuntimeError(f"only saved {len(saved)} images")

        print(json.dumps({"saved": saved}, ensure_ascii=False, indent=2))
    finally:
        browser.close()


if __name__ == "__main__":
    main()
