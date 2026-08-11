#!/usr/bin/env python3
import argparse
import json
import mimetypes
import shutil
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from parse_markdown import parse


def parse_indexes(value: str | None, maximum: int) -> list[int]:
    if not value:
        return []
    indexes = []
    for part in value.split(","):
        index = int(part.strip())
        if index < 1 or index > maximum:
            raise ValueError(f"image index {index} is outside 1..{maximum}")
        if index not in indexes:
            indexes.append(index)
    return indexes


def safe_extension(source: str, content_type: str | None = None) -> str:
    suffix = Path(urlparse(source).path).suffix.lower()
    if suffix in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".tif", ".tiff"}:
        return ".jpg" if suffix == ".jpeg" else suffix
    guessed = mimetypes.guess_extension((content_type or "").split(";", 1)[0].strip())
    return guessed if guessed in {".png", ".jpg", ".webp", ".gif", ".tif", ".tiff"} else ".png"


def collect(item: dict, destination: Path, timeout: float) -> tuple[Path, str]:
    source = item["source"]
    if item["remote"]:
        request = Request(source, headers={"User-Agent": "Mozilla/5.0 punk-xhs-cards/1.0"})
        with urlopen(request, timeout=timeout) as response:
            data = response.read()
            extension = safe_extension(source, response.headers.get("Content-Type"))
        output = destination / f"image-{item['index']:02d}{extension}"
        output.write_bytes(data)
        return output, "downloaded"

    local_value = item.get("resolved_source")
    if not local_value:
        raise ValueError(f"image {item['index']} is not a supported local or remote source")
    local = Path(local_value)
    if not local.is_file():
        raise FileNotFoundError(f"image {item['index']} does not exist: {local}")
    extension = safe_extension(str(local))
    output = destination / f"image-{item['index']:02d}{extension}"
    shutil.copy2(local, output)
    return output, "copied"


def main() -> None:
    parser = argparse.ArgumentParser(description="Copy or download selected Markdown images")
    parser.add_argument("markdown", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--indexes", required=True, help="1-based image indexes, comma separated")
    parser.add_argument("--timeout", type=float, default=20)
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()

    result = parse(args.markdown)
    selected = parse_indexes(args.indexes, len(result["images"]))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest = []
    for index in selected:
        item = result["images"][index - 1]
        output, action = collect(item, args.output_dir, args.timeout)
        manifest.append({**item, "output": str(output.resolve()), "action": action})
        print(output.resolve())

    manifest_path = args.manifest or args.output_dir / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
