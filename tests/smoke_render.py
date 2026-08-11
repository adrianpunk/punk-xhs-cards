#!/usr/bin/env python3
"""Cross-platform smoke test for the Pillow card renderer."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
RENDERER = ROOT / "xhs-ip-cards" / "scripts" / "render_cards.py"


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="xhs-ip-cards-smoke-") as temp_value:
        temp = Path(temp_value)
        profile_dir = temp / "profile"
        profile_dir.mkdir()
        pose = Image.new("RGBA", (320, 480), (0, 0, 0, 0))
        pose_draw = ImageDraw.Draw(pose)
        pose_draw.ellipse((80, 20, 240, 180), fill=(40, 35, 32, 255))
        pose_draw.rounded_rectangle((45, 160, 275, 455), radius=60, fill=(200, 55, 42, 255))
        pose.save(profile_dir / "pose.png")
        hero = Image.new("RGB", (1600, 900), (247, 242, 234))
        hero_draw = ImageDraw.Draw(hero)
        hero_draw.rounded_rectangle((350, 220, 1250, 680), radius=80, fill=(45, 42, 40))
        hero_draw.rectangle((350, 420, 1250, 480), fill=(200, 55, 42))
        hero.save(temp / "hero.png")
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
            "schema_version": 2,
            "slug": "demo",
            "name": "Demo",
            "card_action": "站立讲解",
            "status": "confirmed",
            "assets": {"card_pose": "pose.png", "theme": "theme.json"}
        })
        write_json(temp / "cards.json", {
            "handle": "@demo",
            "cover": {"title": "跨平台知识卡片渲染测试", "author": "Demo", "hero": "hero.png"},
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
        print("Cross-platform renderer smoke test passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
