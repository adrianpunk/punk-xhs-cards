#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlparse


TITLE_FRONTMATTER = re.compile(r"^\s*title\s*:\s*[\"']?(.+?)[\"']?\s*$", re.I)
H1 = re.compile(r"^\s*#\s+(.+?)\s*$")
MARKDOWN_IMAGE = re.compile(r"!\[([^\]]*)\]\(\s*(?:<([^>]+)>|([^\s)]+))(?:\s+[\"']([^\"']*)[\"'])?\s*\)")
HTML_IMAGE = re.compile(r"<img\b[^>]*?\bsrc\s*=\s*[\"']([^\"']+)[\"'][^>]*>", re.I)
HTML_ALT = re.compile(r"\balt\s*=\s*[\"']([^\"']*)[\"']", re.I)
KEY_SIGNALS = ("截图", "图表", "流程", "架构", "步骤", "结果", "验证", "对比", "示意", "效果", "界面", "终端", "仓库", "代码", "点击", "输入", "选择", "打开", "运行", "配置", "安装", "创建", "完成后", "页面显示", "diagram", "chart", "result", "screenshot", "before", "after")
DECORATIVE_SIGNALS = ("头像", "logo", "封面", "装饰", "二维码", "表情", "avatar", "cover", "emoji", "watermark")


def plain_text(value: str) -> str:
    value = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", value)
    value = re.sub(r"<[^>]+>", "", value)
    value = re.sub(r"^[>*_`#\-\s]+|[>*_`#\-\s]+$", "", value.strip())
    return re.sub(r"\s+", " ", value).strip()


def nearby_context(lines: list[str], index: int) -> tuple[str, str]:
    before = ""
    after = ""
    for candidate in range(index - 1, max(-1, index - 4), -1):
        text = plain_text(lines[candidate])
        if text:
            before = text
            break
    for candidate in range(index + 1, min(len(lines), index + 4)):
        text = plain_text(lines[candidate])
        if text:
            after = text
            break
    return before, after


def resolved_source(source: str, markdown_path: Path) -> tuple[str | None, bool]:
    parsed = urlparse(source)
    if parsed.scheme in ("http", "https"):
        return None, True
    if parsed.scheme == "data":
        return None, False
    if parsed.scheme == "file":
        return unquote(parsed.path), False
    local = Path(unquote(source))
    if not local.is_absolute():
        local = markdown_path.parent / local
    return str(local.resolve()), False


def image_inventory(lines: list[str], markdown_path: Path) -> list[dict]:
    images: list[dict] = []
    seen: set[str] = set()
    for line_index, line in enumerate(lines):
        matches: list[tuple[str, str, str | None]] = []
        for match in MARKDOWN_IMAGE.finditer(line):
            matches.append((match.group(1).strip(), (match.group(2) or match.group(3)).strip(), match.group(4)))
        for match in HTML_IMAGE.finditer(line):
            tag = match.group(0)
            alt_match = HTML_ALT.search(tag)
            matches.append(((alt_match.group(1).strip() if alt_match else ""), match.group(1).strip(), None))

        before, after = nearby_context(lines, line_index)
        for alt, source, title in matches:
            context = " ".join(part for part in (alt, title or "", before, after) if part).strip()
            lower_context = context.lower()
            duplicate = source in seen
            seen.add(source)
            decorative = any(signal in lower_context for signal in DECORATIVE_SIGNALS)
            key_signal = any(signal in lower_context for signal in KEY_SIGNALS)
            near_opening = line_index < 10
            if duplicate:
                hint, reason = "skip", "重复图片"
            elif decorative:
                hint, reason = "skip", "上下文显示为装饰、头像、Logo 或封面"
            elif near_opening and not alt and not key_signal:
                hint, reason = "review", "靠近文章开头且缺少说明，可能是原始封面"
            elif key_signal:
                hint, reason = "keep", "上下文包含步骤、截图、图表、结果或验证信号"
            else:
                hint, reason = "review", "需要结合全文与图片内容判断"
            local, remote = resolved_source(source, markdown_path)
            images.append({
                "index": len(images) + 1,
                "line": line_index + 1,
                "alt": alt,
                "title": title,
                "source": source,
                "resolved_source": local,
                "remote": remote,
                "context_before": before,
                "context_after": after,
                "selection_hint": hint,
                "selection_reason": reason,
            })
    return images


def parse(path: Path) -> dict:
    source = path.read_text(encoding="utf-8")
    lines = source.splitlines()

    title = None
    in_frontmatter = bool(lines and lines[0].strip() == "---")
    if in_frontmatter:
        for line in lines[1:]:
            if line.strip() == "---":
                break
            match = TITLE_FRONTMATTER.match(line)
            if match:
                title = match.group(1).strip()
                break

    if not title:
        for line in lines:
            match = H1.match(line)
            if match:
                title = match.group(1).strip()
                break

    return {
        "source": str(path.resolve()),
        "title": title,
        "images": image_inventory(lines, path),
        "cleaned_markdown": source.rstrip() + "\n",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract title and image inventory from Markdown")
    parser.add_argument("markdown", type=Path)
    parser.add_argument("--write-clean", type=Path)
    args = parser.parse_args()

    result = parse(args.markdown)
    if args.write_clean:
        args.write_clean.parent.mkdir(parents=True, exist_ok=True)
        args.write_clean.write_text(result["cleaned_markdown"], encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
