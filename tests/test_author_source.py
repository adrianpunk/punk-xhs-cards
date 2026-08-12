#!/usr/bin/env python3
"""Verify that cover authors come from character/profile data, never Markdown."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "punk-xhs-cards" / "scripts"


def run_json(*arguments: str) -> dict:
    completed = subprocess.run(
        [sys.executable, *arguments],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def run_failed(*arguments: str) -> str:
    completed = subprocess.run(
        [sys.executable, *arguments],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode != 0
    return completed.stderr


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="punk-xhs-author-") as temp_value:
        temp = Path(temp_value)
        markdown = temp / "article.md"
        markdown.write_text(
            "---\ntitle: 测试文章\nauthor: Markdown Author\n---\n\n# 备用标题\n\n正文。\n\n作者：另一个名字\n",
            encoding="utf-8",
        )
        parsed = run_json(str(SCRIPTS / "parse_markdown.py"), str(markdown))
        assert parsed["title"] == "测试文章"
        assert "author" not in parsed
        assert "author_line" not in parsed
        assert "作者：另一个名字" in parsed["cleaned_markdown"]

        assets = temp / "assets"
        assets.mkdir()
        for filename in ("sheet.png", "clean.png", "pose.png"):
            (assets / filename).write_bytes(b"asset")
        (assets / "spec.md").write_text("# Spec\n", encoding="utf-8")
        (assets / "theme.json").write_text(
            json.dumps({"profileName": "Theme Fallback"}, ensure_ascii=False),
            encoding="utf-8",
        )

        character_root = temp / "characters-runtime"
        character = run_json(
            str(SCRIPTS / "character_registry.py"), "register",
            "--root", str(character_root), "--slug", "demo", "--name", "封面作者",
            "--theme-color", "#3366AA",
            "--sheet", str(assets / "sheet.png"),
            "--clean-reference", str(assets / "clean.png"),
            "--spec", str(assets / "spec.md"),
        )
        assert character["author_name"] == "封面作者"
        assert character["theme_color"] == "#3366AA"
        error = run_failed(
            str(SCRIPTS / "character_registry.py"), "register",
            "--root", str(character_root), "--slug", "bad-color", "--name", "Bad",
            "--theme-color", "red",
            "--sheet", str(assets / "sheet.png"),
            "--clean-reference", str(assets / "clean.png"),
            "--spec", str(assets / "spec.md"),
        )
        assert "#RRGGBB" in error

        profile_root = temp / "profiles-runtime"
        profile = run_json(
            str(SCRIPTS / "profile_registry.py"), "register",
            "--root", str(profile_root), "--slug", "demo", "--name", "Demo Profile",
            "--author-name", character["author_name"], "--action", "站立讲解",
            "--sheet", str(assets / "sheet.png"),
            "--clean-reference", str(assets / "clean.png"),
            "--card-pose", str(assets / "pose.png"),
            "--spec", str(assets / "spec.md"),
            "--theme", str(assets / "theme.json"),
        )
        assert profile["author_name"] == "封面作者"
        assert profile["schema_version"] == 3

    print("Author-source test passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
