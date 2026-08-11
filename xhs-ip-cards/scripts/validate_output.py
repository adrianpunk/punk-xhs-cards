#!/usr/bin/env python3
import json
import struct
import sys
from pathlib import Path


def png_size(path: Path):
    data = path.read_bytes()[:24]
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise ValueError("not a valid PNG")
    return struct.unpack(">II", data[16:24])


def fail(message: str):
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


if len(sys.argv) != 4:
    fail("Usage: validate_output.py <cards.json> <output-dir> <publish-copy.md>")

json_path = Path(sys.argv[1])
output_dir = Path(sys.argv[2])
copy_path = Path(sys.argv[3])

try:
    payload = json.loads(json_path.read_text(encoding="utf-8"))
except Exception as exc:
    fail(f"cannot read cards JSON: {exc}")

cards = payload.get("cards")
if not isinstance(cards, list) or not cards:
    fail("cards must be a non-empty array")

cover = payload.get("cover")
if not isinstance(cover, dict):
    fail("cover must be present and separate from cards")
for field in ("title", "author", "hero"):
    if not isinstance(cover.get(field), str) or not cover[field].strip():
        fail(f"cover.{field} is missing")
hero_path = Path(cover["hero"])
if not hero_path.is_absolute():
    hero_path = json_path.parent / hero_path
if not hero_path.is_file():
    fail(f"cover.hero does not exist: {hero_path}")
if any(card.get("kind") == "cover" for card in cards if isinstance(card, dict)):
    fail("cards must contain inner content only; cover is a separate top-level object")

referenced_images = set()
for card_index, card in enumerate(cards, start=1):
    for block_index, block in enumerate(card.get("blocks") or [], start=1):
        if not isinstance(block, dict) or block.get("kind") != "image":
            continue
        value = block.get("path")
        if not isinstance(value, str) or not value.strip():
            fail(f"card {card_index} block {block_index}: image.path is missing")
        image_path = Path(value)
        if not image_path.is_absolute():
            image_path = json_path.parent / image_path
        if not image_path.is_file():
            fail(f"card {card_index} block {block_index}: image does not exist: {image_path}")
        referenced_images.add(image_path.resolve())

manifest_path = json_path.parent / "assets" / "article-images" / "manifest.json"
if manifest_path.is_file():
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"cannot read article image manifest: {exc}")
    if not isinstance(manifest, list):
        fail("article image manifest must be an array")
    for item in manifest:
        value = item.get("output") if isinstance(item, dict) else None
        if not isinstance(value, str) or not value.strip():
            fail("article image manifest contains an item without output")
        selected_path = Path(value)
        if not selected_path.is_absolute():
            selected_path = manifest_path.parent / selected_path
        if selected_path.resolve() not in referenced_images:
            fail(f"selected Markdown image is missing from cards: {selected_path}")

expected = len(cards)
images = sorted(output_dir.glob("card-*.png"))
if len(images) != expected:
    fail(f"expected {expected} PNG files, found {len(images)}")

cover_image = output_dir / "cover.png"
if not cover_image.exists():
    fail("cover.png is missing")

try:
    cover_size = png_size(cover_image)
except Exception as exc:
    fail(f"cover.png: {exc}")
if cover_size != (1080, 1440):
    fail(f"cover.png: expected 1080x1440, got {cover_size[0]}x{cover_size[1]}")

for image in images:
    try:
        size = png_size(image)
    except Exception as exc:
        fail(f"{image.name}: {exc}")
    if size != (1080, 1440):
        fail(f"{image.name}: expected 1080x1440, got {size[0]}x{size[1]}")

if not copy_path.exists() or copy_path.stat().st_size < 80:
    fail("publish-copy.md is missing or too short")

copy = copy_path.read_text(encoding="utf-8")
for marker in ("# 推荐标题", "# 正文", "# Tags"):
    if marker not in copy:
        fail(f"publish-copy.md is missing section: {marker}")

print(f"VALID: 1 unnumbered cover + {expected} inner cards, all 1080x1440, publish copy present")
