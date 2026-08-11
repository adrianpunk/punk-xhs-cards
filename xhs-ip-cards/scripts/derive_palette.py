#!/usr/bin/env python3
"""Derive a restrained card palette from a character image."""

from __future__ import annotations

import argparse
import colorsys
import json
import re
import sys
from collections import defaultdict
from pathlib import Path


HEX_RE = re.compile(r"^#?[0-9a-fA-F]{6}$")


def parse_hex(value: str) -> tuple[int, int, int]:
    if not HEX_RE.fullmatch(value):
        raise ValueError("accent must be a six-digit hex color such as #C9362B")
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def to_hex(rgb: tuple[int, int, int]) -> str:
    return "#" + "".join(f"{max(0, min(255, c)):02X}" for c in rgb)


def mix(a: tuple[int, int, int], b: tuple[int, int, int], amount: float) -> tuple[int, int, int]:
    return tuple(round(a[i] * (1 - amount) + b[i] * amount) for i in range(3))


def normalize_accent(rgb: tuple[int, int, int]) -> tuple[int, int, int]:
    h, s, v = colorsys.rgb_to_hsv(*(c / 255 for c in rgb))
    s = max(0.50, min(0.78, s))
    v = max(0.58, min(0.76, v))
    return tuple(round(c * 255) for c in colorsys.hsv_to_rgb(h, s, v))


def derive_from_image(path: Path) -> tuple[tuple[int, int, int], str]:
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("Pillow is required: install with `uv pip install pillow`") from exc

    image = Image.open(path).convert("RGBA")
    image.thumbnail((320, 320))
    bins: dict[tuple[int, int, int], list[float]] = defaultdict(lambda: [0.0, 0.0, 0.0, 0.0])

    pixels = image.get_flattened_data() if hasattr(image, "get_flattened_data") else image.getdata()
    for r, g, b, a in pixels:
        if a < 80:
            continue
        rf, gf, bf = r / 255, g / 255, b / 255
        h, s, v = colorsys.rgb_to_hsv(rf, gf, bf)
        if v < 0.14 or v > 0.94 or s < 0.26:
            continue
        # Exclude common skin range while retaining true reds and saturated yellows.
        if 0.035 <= h <= 0.13 and 0.18 <= s <= 0.72 and v >= 0.38:
            continue
        key = (r // 32, g // 32, b // 32)
        weight = (s ** 1.45) * (0.45 + min(v, 0.82)) * (a / 255)
        item = bins[key]
        item[0] += weight
        item[1] += r * weight
        item[2] += g * weight
        item[3] += b * weight

    if not bins:
        return (122, 112, 104), "fallback"

    best = max(bins.values(), key=lambda item: item[0])
    if best[0] < 2.0:
        return (122, 112, 104), "fallback"
    return tuple(round(best[i] / best[0]) for i in (1, 2, 3)), "derived"


def main() -> int:
    parser = argparse.ArgumentParser(description="Derive a card theme from a character image")
    parser.add_argument("--image", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--profile-name", required=True)
    parser.add_argument("--handle", default="")
    parser.add_argument("--brand-label", default="NOTES")
    parser.add_argument("--accent")
    args = parser.parse_args()

    try:
        image_path = Path(args.image).expanduser().resolve()
        if not image_path.is_file():
            raise FileNotFoundError(f"Missing image: {image_path}")
        if args.accent:
            raw, source = parse_hex(args.accent), "user"
        else:
            raw, source = derive_from_image(image_path)
        accent = raw if source == "fallback" else normalize_accent(raw)
        h, s, v = colorsys.rgb_to_hsv(*(c / 255 for c in accent))
        deep = tuple(round(c * 255) for c in colorsys.hsv_to_rgb(h, min(0.90, s + 0.10), max(0.34, v * 0.56)))
        paper_base = (250, 247, 240)
        palette = {
            "accent": to_hex(accent),
            "deepAccent": to_hex(deep),
            "panel": to_hex(mix(accent, (255, 255, 255), 0.86)),
            "paper": to_hex(mix(paper_base, accent, 0.025)),
            "ink": "#1D1815",
            "body": "#453E39",
            "muted": "#81766E",
            "line": to_hex(mix(accent, (255, 255, 255), 0.72)),
        }
        result = {
            "schemaVersion": 1,
            "profileName": args.profile_name,
            "handle": args.handle,
            "brandLabel": args.brand_label or "NOTES",
            "source": source,
            "palette": palette,
        }
        output = Path(args.out).expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
