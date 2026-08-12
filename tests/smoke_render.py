#!/usr/bin/env python3
"""Cross-platform smoke test for the Pillow card renderer."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from contextlib import nullcontext
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
RENDERER = ROOT / "punk-xhs-cards" / "scripts" / "render_cards.py"


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    keep = os.environ.get("PUNK_XHS_SMOKE_OUTPUT")
    context = nullcontext(keep) if keep else tempfile.TemporaryDirectory(prefix="punk-xhs-cards-smoke-")
    with context as temp_value:
        temp = Path(temp_value)
        temp.mkdir(parents=True, exist_ok=True)
        profile_dir = temp / "profile"
        profile_dir.mkdir()
        pose = Image.new("RGBA", (320, 480), (0, 0, 0, 0))
        pose_draw = ImageDraw.Draw(pose)
        pose_draw.ellipse((80, 20, 240, 180), fill=(40, 35, 32, 255))
        pose_draw.rounded_rectangle((45, 160, 275, 455), radius=60, fill=(200, 55, 42, 255))
        pose.save(profile_dir / "pose.png")
        illustration = Image.new("RGB", (1200, 675), (247, 242, 234))
        illustration_draw = ImageDraw.Draw(illustration)
        illustration_draw.rounded_rectangle((220, 100, 980, 575), radius=80, fill=(45, 42, 40))
        illustration_draw.rectangle((220, 300, 980, 370), fill=(200, 55, 42))
        illustration.save(temp / "cover-illustration.png")
        screenshot = Image.new("RGB", (1200, 700), (238, 238, 238))
        screenshot_draw = ImageDraw.Draw(screenshot)
        screenshot_draw.rounded_rectangle((100, 80, 1100, 620), radius=24, fill=(38, 38, 38))
        screenshot.save(temp / "screenshot.png")
        write_json(profile_dir / "theme.json", {
            "schemaVersion": 1,
            "profileName": "Demo",
            "handle": "@demo",
            "brandLabel": "Demo",
            "palette": {
                "accent": "#D4382A", "deepAccent": "#9F2319", "panel": "#F7E6E1",
                "paper": "#FAF7F0", "ink": "#211815", "body": "#514641",
                "muted": "#8A7D75", "line": "#E7CCC4"
            }
        })
        write_json(profile_dir / "profile.json", {
            "schema_version": 3,
            "slug": "demo",
            "name": "Demo",
            "author_name": "Demo Author",
            "card_action": "站立讲解",
            "status": "confirmed",
            "assets": {"card_pose": "pose.png", "theme": "theme.json"}
        })
        write_json(temp / "cards.json", {
            "handle": "@demo",
            "cover": {"title": "跨平台知识卡片渲染测试", "illustration": "cover-illustration.png"},
            "cards": [{
                "kind": "content",
                "eyebrow": "01 · 跨平台",
                "title": "Windows、Linux 与 macOS 共用一套版式",
                "blocks": [
                    {"kind": "paragraph", "text": "同一份数据应该得到相同尺寸和结构的图片。"},
                    {"kind": "image", "path": "screenshot.png", "caption": "关键截图测试", "height": 360},
                    {"kind": "highlight", "text": "渲染完成后继续检查尺寸与文件。"}
                ]
            }]
        })
        check_command = [sys.executable, str(RENDERER), "--check"]
        render_command = [
            sys.executable, str(RENDERER), str(temp / "cards.json"),
            str(temp / "output"), str(profile_dir / "profile.json")
        ]
        font = os.environ.get("XHS_IP_CARDS_FONT")
        if font:
            check_command += ["--font", font]
            render_command += ["--font", font]
        subprocess.run(check_command, check=True)
        subprocess.run(render_command, check=True)
        for name in ("cover.png", "card-01.png"):
            path = temp / "output" / name
            if not path.is_file():
                raise AssertionError(f"Missing output: {name}")
            with Image.open(path) as result:
                if result.size != (1080, 1440):
                    raise AssertionError(f"Unexpected size for {name}: {result.size}")
        with Image.open(temp / "output" / "cover.png") as cover:
            rgba = cover.convert("RGBA")
            accent = (212, 56, 42, 255)
            # The new cover has no title panel: the upper corners remain theme color.
            assert rgba.getpixel((70, 70)) == accent
            # The macOS window contains a full 16:9 artwork area below the toolbar.
            assert rgba.getpixel((80, 395)) != accent
            assert rgba.getpixel((1000, 905)) != accent
            # The lower cover is clean theme color except for the centered author name.
            assert rgba.getpixel((100, 1120)) == accent
        print("Cross-platform renderer smoke test passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
