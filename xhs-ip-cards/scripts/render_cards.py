#!/usr/bin/env python3
"""Render XHS IP cards consistently on macOS, Windows, and Linux."""

from __future__ import annotations

import argparse
import json
import os
import platform
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

try:
    from PIL import Image, ImageDraw, ImageFont, __version__ as PILLOW_VERSION
except ImportError as exc:  # pragma: no cover - exercised by runtime setup
    print(
        "ERROR: Pillow is required. Install it with: python -m pip install -r requirements.txt",
        file=sys.stderr,
    )
    raise SystemExit(5) from exc


W = 1080
H = 1440
MEASURE_IMAGE = Image.new("RGB", (8, 8), "white")
MEASURE_DRAW = ImageDraw.Draw(MEASURE_IMAGE)


def hex_color(value: str, alpha: int = 255) -> tuple[int, int, int, int]:
    clean = value.strip().lstrip("#")
    if len(clean) != 6:
        raise ValueError(f"Invalid theme color: {value}")
    return tuple(int(clean[index:index + 2], 16) for index in (0, 2, 4)) + (alpha,)


def existing(paths: list[str | Path]) -> Path | None:
    for value in paths:
        path = Path(value).expanduser()
        if path.is_file():
            return path.resolve()
    return None


def linux_font_candidates(bold: bool = False) -> list[Path]:
    roots = [Path("/usr/share/fonts"), Path("/usr/local/share/fonts")]
    names = (
        ["NotoSansCJK-Bold.ttc", "NotoSansSC-Bold.otf", "SourceHanSansSC-Bold.otf"]
        if bold
        else ["NotoSansCJK-Regular.ttc", "NotoSansSC-Regular.otf", "SourceHanSansSC-Regular.otf", "wqy-zenhei.ttc"]
    )
    found: list[Path] = []
    for root in roots:
        if not root.is_dir():
            continue
        for name in names:
            found.extend(sorted(root.rglob(name)))
    return found


def resolve_font_paths(custom_font: str | None, custom_mono: str | None) -> tuple[Path, Path, Path]:
    system = platform.system()
    windir = Path(os.environ.get("WINDIR", "C:/Windows"))
    regular_candidates: list[str | Path] = []
    bold_candidates: list[str | Path] = []
    mono_candidates: list[str | Path] = []
    if custom_font:
        regular_candidates.append(custom_font)
        bold_candidates.append(custom_font)
    env_font = os.environ.get("XHS_IP_CARDS_FONT")
    if env_font:
        regular_candidates.append(env_font)
        bold_candidates.append(env_font)
    if system == "Darwin":
        regular_candidates += [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
        ]
        bold_candidates += [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Medium.ttc",
        ]
        mono_candidates += ["/System/Library/Fonts/SFNSMono.ttf", "/System/Library/Fonts/Menlo.ttc"]
    elif system == "Windows":
        regular_candidates += [windir / "Fonts/msyh.ttc", windir / "Fonts/simhei.ttf"]
        bold_candidates += [windir / "Fonts/msyhbd.ttc", windir / "Fonts/msyh.ttc", windir / "Fonts/simhei.ttf"]
        mono_candidates += [windir / "Fonts/consola.ttf", windir / "Fonts/cour.ttf"]
    else:
        regular_candidates += linux_font_candidates(False)
        bold_candidates += linux_font_candidates(True) + linux_font_candidates(False)
        mono_candidates += [
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf",
        ]
    if custom_mono:
        mono_candidates.insert(0, custom_mono)
    env_mono = os.environ.get("XHS_IP_CARDS_MONO_FONT")
    if env_mono:
        mono_candidates.insert(0, env_mono)
    regular = existing(regular_candidates)
    bold = existing(bold_candidates)
    if regular is None:
        raise RuntimeError(
            "No Chinese font found. Install Noto Sans CJK on Linux, use Microsoft YaHei on Windows, "
            "or pass --font /path/to/font.ttf."
        )
    if bold is None:
        bold = regular
    mono = existing(mono_candidates) or regular
    return regular, bold, mono


class Fonts:
    def __init__(self, regular: Path, bold: Path, mono: Path):
        self.regular = regular
        self.bold = bold
        self.mono = mono

    @lru_cache(maxsize=128)
    def get(self, size: int, weight: str = "regular", mono: bool = False) -> ImageFont.FreeTypeFont:
        path = self.mono if mono else (self.bold if weight in {"medium", "semibold", "bold", "heavy"} else self.regular)
        return ImageFont.truetype(str(path), size=size)


class Renderer:
    def __init__(self, theme: dict[str, Any], fonts: Fonts):
        palette = theme["palette"]
        self.paper = hex_color(palette["paper"])
        self.panel = hex_color(palette["panel"])
        self.accent = hex_color(palette["accent"])
        self.deep = hex_color(palette["deepAccent"])
        self.ink = hex_color(palette["ink"])
        self.body = hex_color(palette["body"])
        self.muted = hex_color(palette["muted"])
        self.line = hex_color(palette["line"])
        self.fonts = fonts

    @staticmethod
    def _box(box: tuple[float, float, float, float]) -> tuple[int, int, int, int]:
        x, y, width, height = box
        return round(x), round(y), round(x + width), round(y + height)

    def fill(self, draw: ImageDraw.ImageDraw, box: tuple[float, float, float, float], color: tuple[int, int, int, int], radius: int = 0) -> None:
        coords = self._box(box)
        if radius:
            draw.rounded_rectangle(coords, radius=radius, fill=color)
        else:
            draw.rectangle(coords, fill=color)

    def stroke(self, draw: ImageDraw.ImageDraw, box: tuple[float, float, float, float], color: tuple[int, int, int, int], width: int = 2, radius: int = 0) -> None:
        draw.rounded_rectangle(self._box(box), radius=radius, outline=color, width=width)

    @staticmethod
    def rule(draw: ImageDraw.ImageDraw, x1: float, y1: float, x2: float, y2: float, color: tuple[int, int, int, int], width: int = 2) -> None:
        draw.line((round(x1), round(y1), round(x2), round(y2)), fill=color, width=width)

    @staticmethod
    def measure(value: str, font: ImageFont.FreeTypeFont) -> float:
        return float(MEASURE_DRAW.textlength(value, font=font))

    def wrap(self, value: str, font: ImageFont.FreeTypeFont, width: float) -> list[str]:
        lines: list[str] = []
        for paragraph in value.replace("\r\n", "\n").split("\n"):
            if not paragraph:
                lines.append("")
                continue
            current = ""
            for character in paragraph:
                candidate = current + character
                if current and self.measure(candidate, font) > width:
                    lines.append(current.rstrip())
                    current = character.lstrip() if character.isspace() else character
                else:
                    current = candidate
            lines.append(current.rstrip())
        return lines or [""]

    @staticmethod
    def line_height(font: ImageFont.FreeTypeFont, size: int) -> int:
        box = font.getbbox("Ag国")
        return max(round(size * 1.16), box[3] - box[1])

    def text_height(self, value: str, width: float, size: float, weight: str = "regular", spacing: float = 7, mono: bool = False) -> float:
        size_i = round(size)
        font = self.fonts.get(size_i, weight, mono)
        lines = self.wrap(value, font, width)
        return len(lines) * self.line_height(font, size_i) + max(0, len(lines) - 1) * spacing

    def text(self, draw: ImageDraw.ImageDraw, value: str, box: tuple[float, float, float, float], size: float,
             weight: str = "regular", color: tuple[int, int, int, int] | None = None,
             align: str = "left", spacing: float = 7, mono: bool = False) -> None:
        x, y, width, _ = box
        size_i = round(size)
        font = self.fonts.get(size_i, weight, mono)
        lines = self.wrap(value, font, width)
        cursor = float(y)
        step = self.line_height(font, size_i) + spacing
        for line in lines:
            line_width = self.measure(line, font)
            if align == "center":
                tx = x + (width - line_width) / 2
            elif align == "right":
                tx = x + width - line_width
            else:
                tx = x
            bbox = font.getbbox(line or " ")
            draw.text((round(tx), round(cursor - bbox[1])), line, font=font, fill=color or self.body)
            cursor += step

    @staticmethod
    def open_image(path: Path) -> Image.Image:
        if not path.is_file():
            raise FileNotFoundError(f"Missing image: {path}")
        with Image.open(path) as source:
            return source.convert("RGBA")

    @staticmethod
    def aspect_fit(canvas: Image.Image, source: Image.Image, box: tuple[float, float, float, float]) -> None:
        x, y, width, height = map(round, box)
        image = source.copy()
        image.thumbnail((max(1, width), max(1, height)), Image.Resampling.LANCZOS)
        px = x + (width - image.width) // 2
        py = y + height - image.height
        canvas.alpha_composite(image, (px, py))

    def block_height(self, block: dict[str, Any]) -> float:
        kind = block.get("kind")
        if kind == "paragraph":
            return self.text_height(block.get("text", ""), 952, 24.5, spacing=9) + 18
        if kind in {"highlight", "note"}:
            return max(82, self.text_height(block.get("text", ""), 882, 23.5, "semibold", 6) + 38) + 18
        if kind == "section":
            return 68
        if kind == "item":
            body = self.text_height(block.get("body", ""), 830, 22.5, spacing=6)
            return max(98, 48 + body + 22)
        if kind == "bullet":
            return max(48, self.text_height(block.get("text", ""), 900, 23.5, spacing=6) + 16)
        if kind == "code":
            return max(76, self.text_height(block.get("text", ""), 900, 18.5, "medium", 7, True) + 34) + 16
        if kind == "image":
            media = min(520, max(220, float(block.get("height", 360))))
            caption = block.get("caption", "")
            caption_height = self.text_height(caption, 900, 18.5, spacing=4) + 22 if caption else 0
            return media + caption_height + 18
        if kind == "spacer":
            return float(block.get("height", 16))
        return 0

    def draw_block(self, canvas: Image.Image, draw: ImageDraw.ImageDraw, block: dict[str, Any], y: float, asset_base: Path) -> None:
        kind = block.get("kind")
        height = self.block_height(block)
        if kind == "paragraph":
            self.text(draw, block.get("text", ""), (64, y, 952, height - 8), 24.5, color=self.body, spacing=9)
        elif kind == "highlight":
            self.fill(draw, (64, y, 952, height - 18), self.panel, 18)
            self.fill(draw, (64, y, 8, height - 18), self.accent, 4)
            self.text(draw, block.get("text", ""), (94, y + 19, 882, height - 42), 23.5, "semibold", self.deep, spacing=6)
        elif kind == "note":
            self.fill(draw, (64, y, 952, height - 18), self.panel, 18)
            self.stroke(draw, (64, y, 952, height - 18), self.line, 2, 18)
            self.text(draw, block.get("text", ""), (90, y + 19, 892, height - 42), 23.5, "semibold", self.deep, spacing=6)
        elif kind == "section":
            self.fill(draw, (64, y + 8, 7, 38), self.accent, 3)
            self.text(draw, block.get("text", ""), (88, y, 900, 52), 30, "bold", self.ink, spacing=0)
        elif kind == "item":
            self.fill(draw, (64, y + 2, 54, 54), self.panel, 27)
            self.text(draw, block.get("number", "•"), (64, y + 13, 54, 28), 18, "bold", self.deep, "center", 0, True)
            self.text(draw, block.get("title", ""), (140, y, 850, 42), 28, "bold", self.ink, spacing=0)
            self.text(draw, block.get("body", ""), (140, y + 47, 850, height - 65), 22.5, color=self.body, spacing=6)
            self.rule(draw, 140, y + height - 8, 1016, y + height - 8, self.line)
        elif kind == "bullet":
            self.fill(draw, (76, y + 14, 10, 10), self.accent, 5)
            self.text(draw, block.get("text", ""), (101, y, 905, height), 23.5, color=self.body, spacing=6)
        elif kind == "code":
            self.fill(draw, (64, y, 952, height - 16), self.panel, 16)
            self.text(draw, block.get("text", ""), (88, y + 17, 904, height - 42), 18.5, "medium", self.ink, spacing=7, mono=True)
        elif kind == "image":
            value = block.get("path")
            if not value:
                raise ValueError("Image block is missing path")
            path = Path(value).expanduser()
            if not path.is_absolute():
                path = asset_base / path
            source = self.open_image(path.resolve())
            media = min(520, max(220, float(block.get("height", 360))))
            self.fill(draw, (64, y, 952, media), (255, 255, 255, 230), 16)
            self.stroke(draw, (64, y, 952, media), self.line, 2, 16)
            self.aspect_fit(canvas, source, (78, y + 14, 924, media - 28))
            caption = block.get("caption", "")
            if caption:
                self.text(draw, caption, (82, y + media + 10, 916, height - media - 18), 18.5, color=self.muted, spacing=4)

    def footer(self, canvas: Image.Image, draw: ImageDraw.ImageDraw, page: int, total: int, handle: str, brand: str, ip: Image.Image) -> None:
        self.rule(draw, 64, 1238, 742, 1238, self.line)
        self.text(draw, brand.upper(), (64, 1270, 360, 30), 19, "semibold", self.accent, spacing=0)
        self.text(draw, handle, (64, 1308, 330, 30), 20, "medium", self.muted, spacing=0)
        self.text(draw, f"{page:02d} / {total:02d}", (64, 1365, 190, 28), 18, "medium", self.muted, spacing=0, mono=True)
        self.aspect_fit(canvas, ip, (785, 1172, 250, 225))

    def single_title_size(self, value: str, max_width: float) -> int:
        for size in range(48, 19, -1):
            if self.measure(value, self.fonts.get(size, "semibold")) <= max_width:
                return size
        return 20

    @staticmethod
    def balanced_title(value: str) -> str:
        characters = list(value)
        if len(characters) < 12:
            return value
        separators = set("：:，,；;。！？!?、—- ")
        candidates: list[tuple[int, int]] = []
        for index in range(1, len(characters)):
            previous = characters[index - 1]
            if previous in separators and index >= 5 and len(characters) - index >= 5:
                bonus = -8 if previous in "：:" else 0
                candidates.append((abs(len(characters) - index * 2) + bonus, index))
        split = min(candidates)[1] if candidates else len(characters) // 2
        first = "".join(characters[:split]).strip()
        second = "".join(characters[split:]).strip()
        return value if not first or not second else first + "\n" + second

    def draw_book_cover(self, cover: dict[str, Any], handle: str, hero: Image.Image, ip: Image.Image) -> Image.Image:
        canvas = Image.new("RGBA", (W, H), self.paper)
        draw = ImageDraw.Draw(canvas)
        self.fill(draw, (0, 0, 38, H), self.deep)
        self.fill(draw, (38, 842, W - 38, H - 842), self.deep)
        self.fill(draw, (78, 54, 954, 566), (255, 255, 255, 250), 18)
        self.stroke(draw, (78, 54, 954, 566), self.line, 2, 18)
        self.aspect_fit(canvas, hero, (90, 66, 930, 542))
        draw.polygon([(38, 654), (1080, 654), (1080, 842), (735, 842), (610, 955), (38, 955)], fill=self.paper)
        self.rule(draw, 38, 654, 1080, 654, self.accent, 2)
        title = str(cover["title"]).replace("\n", " ")
        fitted = self.single_title_size(title, 900)
        if fitted >= 46:
            self.text(draw, title, (84, 702, 900, 72), fitted, "semibold", self.ink, spacing=0)
        else:
            arranged = self.balanced_title(title)
            lines = arranged.split("\n")
            size = 52
            while size > 36 and max(self.measure(line, self.fonts.get(size, "semibold")) for line in lines) > 900:
                size -= 1
            self.text(draw, arranged, (84, 662, 900, 174), size, "semibold", self.ink, spacing=5)
        self.rule(draw, 84, 832, 646, 832, self.accent, 3)
        self.fill(draw, (84, 862, 8, 42), self.accent, 3)
        self.text(draw, "作者", (112, 867, 80, 30), 19, "semibold", self.accent, spacing=0)
        self.text(draw, str(cover["author"]), (198, 860, 430, 42), 29, "semibold", self.ink, spacing=0)
        if handle:
            self.text(draw, handle, (84, 1290, 430, 34), 22, "semibold", self.paper, spacing=0)
            self.rule(draw, 84, 1342, 455, 1342, self.paper[:3] + (102,), 2)
        self.aspect_fit(canvas, ip, (700, 965, 344, 430))
        return canvas

    def draw_legacy_cover(self, card: dict[str, Any], page: int, total: int, handle: str, brand: str, ip: Image.Image) -> Image.Image:
        canvas = Image.new("RGBA", (W, H), self.paper)
        draw = ImageDraw.Draw(canvas)
        self.fill(draw, (0, 0, 18, H), self.accent)
        self.text(draw, card.get("eyebrow") or brand.upper(), (64, 68, 620, 34), 21, "semibold", self.accent, spacing=0)
        self.stroke(draw, (925, 52, 91, 45), self.accent, 2, 22)
        self.text(draw, f"{page:02d}", (925, 60, 91, 28), 19, "bold", self.accent, "center", 0, True)
        title = card["title"]
        self.text(draw, title, (60, 160, 900, 300), 61 if len(title) > 28 else 69, "heavy", self.ink, spacing=6)
        self.rule(draw, 64, 500, 760, 500, self.accent, 4)
        if card.get("subtitle"):
            self.text(draw, card["subtitle"], (64, 540, 790, 68), 39, "semibold", self.deep, spacing=0)
        if card.get("summary"):
            self.text(draw, card["summary"], (64, 650, 720, 190), 25, color=self.body, spacing=10)
        if card.get("highlight"):
            self.fill(draw, (64, 890, 740, 104), self.panel, 18)
            self.fill(draw, (64, 890, 8, 104), self.accent, 4)
            self.text(draw, card["highlight"], (94, 916, 674, 62), 23.5, "semibold", self.deep, spacing=6)
        self.rule(draw, 64, 1240, 650, 1240, self.line)
        signature = brand.upper() if not handle else f"{brand.upper()} · {handle}"
        self.text(draw, signature, (64, 1280, 590, 34), 20, "medium", self.accent, spacing=0)
        self.text(draw, f"{page:02d} / {total:02d}", (64, 1360, 190, 28), 18, "medium", self.muted, spacing=0, mono=True)
        self.aspect_fit(canvas, ip, (620, 790, 410, 570))
        return canvas

    def draw_content(self, card: dict[str, Any], page: int, total: int, handle: str, brand: str, ip: Image.Image, asset_base: Path) -> Image.Image:
        canvas = Image.new("RGBA", (W, H), self.paper)
        draw = ImageDraw.Draw(canvas)
        self.fill(draw, (0, 0, 18, H), self.accent)
        self.fill(draw, (64, 53, 410, 42), self.panel, 21)
        self.text(draw, card.get("eyebrow") or brand.upper(), (82, 61, 380, 26), 18, "semibold", self.deep, spacing=0)
        self.stroke(draw, (925, 48, 91, 45), self.accent, 2, 22)
        self.text(draw, f"{page:02d}", (925, 56, 91, 28), 19, "bold", self.accent, "center", 0, True)
        title = card["title"]
        self.text(draw, title, (64, 132, 940, 166), 49 if len(title) > 30 else 56, "heavy", self.ink, spacing=5)
        self.rule(draw, 64, 312, 1016, 312, self.accent, 4)
        y = 350.0
        for block in card.get("blocks") or []:
            height = self.block_height(block)
            if y + height > 1190:
                raise ValueError(f"Card {page} content overflows by {round(y + height - 1190)} px; reduce or redistribute blocks")
            self.draw_block(canvas, draw, block, y, asset_base)
            y += height
        self.footer(canvas, draw, page, total, handle, brand, ip)
        return canvas


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Missing JSON: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def resolve_asset(base: Path, value: str) -> Path:
    path = Path(value).expanduser()
    return path.resolve() if path.is_absolute() else (base / path).resolve()


def runtime_check(font: str | None, mono_font: str | None) -> int:
    regular, bold, mono = resolve_font_paths(font, mono_font)
    print(json.dumps({
        "platform": platform.system(),
        "python": platform.python_version(),
        "pillow": PILLOW_VERSION,
        "font_regular": str(regular),
        "font_bold": str(bold),
        "font_mono": str(mono),
        "status": "ready",
    }, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render XHS IP cards on macOS, Windows, and Linux")
    parser.add_argument("cards_json", nargs="?")
    parser.add_argument("output_dir", nargs="?")
    parser.add_argument("profile_json", nargs="?")
    parser.add_argument("--allow-draft", action="store_true")
    parser.add_argument("--font", help="Path to a Chinese TrueType/OpenType font")
    parser.add_argument("--mono-font", help="Path to a monospace TrueType/OpenType font")
    parser.add_argument("--check", action="store_true", help="Check Pillow and font availability")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.check:
            return runtime_check(args.font, args.mono_font)
        if not all((args.cards_json, args.output_dir, args.profile_json)):
            raise ValueError("cards_json, output_dir, and profile_json are required unless --check is used")
        input_path = Path(args.cards_json).expanduser().resolve()
        output_dir = Path(args.output_dir).expanduser().resolve()
        profile_path = Path(args.profile_json).expanduser().resolve()
        profile = load_json(profile_path)
        if profile.get("status") != "confirmed" and not args.allow_draft:
            raise ValueError("profile is not confirmed; use --allow-draft for a sample or confirm it first")
        assets = profile.get("assets") or {}
        theme_path = resolve_asset(profile_path.parent, assets["theme"])
        pose_path = resolve_asset(profile_path.parent, assets["card_pose"])
        theme = load_json(theme_path)
        regular, bold, mono = resolve_font_paths(args.font, args.mono_font)
        renderer = Renderer(theme, Fonts(regular, bold, mono))
        ip = renderer.open_image(pose_path)
        payload = load_json(input_path)
        handle = payload.get("handle") or theme.get("handle") or ""
        brand = theme.get("brandLabel") or theme["profileName"]
        output_dir.mkdir(parents=True, exist_ok=True)
        cover = payload.get("cover")
        if cover:
            hero = renderer.open_image(resolve_asset(input_path.parent, cover["hero"]))
            cover_image = renderer.draw_book_cover(cover, handle, hero, ip)
            cover_path = output_dir / "cover.png"
            cover_image.convert("RGB").save(cover_path, "PNG", optimize=True)
            print(cover_path)
        cards = payload.get("cards") or []
        for index, card in enumerate(cards, start=1):
            if card.get("kind") == "cover":
                image = renderer.draw_legacy_cover(card, index, len(cards), handle, brand, ip)
            else:
                image = renderer.draw_content(card, index, len(cards), handle, brand, ip, input_path.parent)
            output_path = output_dir / f"card-{index:02d}.png"
            image.convert("RGB").save(output_path, "PNG", optimize=True)
            print(output_path)
        return 0
    except (FileNotFoundError, KeyError, ValueError, RuntimeError, json.JSONDecodeError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
