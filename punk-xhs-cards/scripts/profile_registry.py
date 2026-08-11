#!/usr/bin/env python3
"""Manage local XHS IP card profiles with no external dependencies."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MANIFEST_NAME = "profile.json"
CURRENT_NAME = "current-profile.json"
LEGACY_CARD_ACTION = "盘腿使用电脑，身体和视线朝向内容区"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def load_json(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(f"Missing file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def validate_slug(slug: str) -> None:
    if not SLUG_RE.fullmatch(slug):
        raise ValueError("slug must use lowercase letters, digits, and single hyphens")


def profile_dir(root: Path, slug: str) -> Path:
    validate_slug(slug)
    return root.resolve() / "profiles" / slug


def next_path(directory: Path, stem: str, suffix: str) -> Path:
    candidate = directory / f"{stem}{suffix}"
    if not candidate.exists():
        return candidate
    version = 2
    while True:
        candidate = directory / f"{stem}-v{version}{suffix}"
        if not candidate.exists():
            return candidate
        version += 1


def copy_versioned(source: Path, directory: Path, stem: str, suffix: str | None = None) -> Path:
    source = source.expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(f"Missing asset: {source}")
    actual_suffix = suffix or source.suffix.lower()
    destination = next_path(directory, stem, actual_suffix)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return destination


def manifest_path(root: Path, slug: str) -> Path:
    return profile_dir(root, slug) / MANIFEST_NAME


def resolved_manifest(root: Path, slug: str, allow_draft: bool = False) -> dict:
    directory = profile_dir(root, slug)
    manifest = load_json(directory / MANIFEST_NAME)
    if manifest.get("status") != "confirmed" and not allow_draft:
        raise ValueError(f"Profile '{slug}' is not confirmed")
    assets = manifest.get("assets", {})
    for key in ("sheet", "clean_reference", "card_pose", "spec", "theme"):
        value = assets.get(key)
        if not value:
            raise ValueError(f"Manifest is missing assets.{key}")
        path = Path(value)
        if not path.is_absolute():
            path = directory / path
        if not path.is_file():
            raise FileNotFoundError(f"Missing {key}: {path}")
        assets[key] = str(path.resolve())
    manifest["assets"] = assets
    action = manifest.get("card_action")
    if not isinstance(action, str) or not action.strip():
        action = LEGACY_CARD_ACTION
    manifest["card_action"] = action.strip()
    manifest["manifest_path"] = str((directory / MANIFEST_NAME).resolve())
    return manifest


def command_register(args: argparse.Namespace) -> None:
    root = Path(args.root).expanduser().resolve()
    directory = profile_dir(root, args.slug)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / MANIFEST_NAME
    old = load_json(path) if path.exists() else {}
    action = args.action.strip()
    if not action:
        raise ValueError("action must not be empty")
    assets = {
        "sheet": copy_versioned(Path(args.sheet), directory, "character-sheet").name,
        "clean_reference": copy_versioned(Path(args.clean_reference), directory, "character-clean").name,
        "card_pose": copy_versioned(Path(args.card_pose), directory, "character-card-pose").name,
        "spec": copy_versioned(Path(args.spec), directory, "character-spec", ".md").name,
        "theme": copy_versioned(Path(args.theme), directory, "theme", ".json").name,
    }
    now = utc_now()
    manifest = {
        "schema_version": 2,
        "slug": args.slug,
        "name": args.name,
        "card_action": action,
        "status": "draft",
        "revision": int(old.get("revision", 0)) + 1,
        "created_at": old.get("created_at", now),
        "updated_at": now,
        "confirmed_at": None,
        "assets": assets,
    }
    write_json(path, manifest)
    print(json.dumps(resolved_manifest(root, args.slug, allow_draft=True), ensure_ascii=False, indent=2))


def command_confirm(args: argparse.Namespace) -> None:
    root = Path(args.root).expanduser().resolve()
    resolved_manifest(root, args.slug, allow_draft=True)
    path = manifest_path(root, args.slug)
    stored = load_json(path)
    now = utc_now()
    stored.update(status="confirmed", updated_at=now, confirmed_at=now)
    write_json(path, stored)
    write_json(root / CURRENT_NAME, {
        "schema_version": 1,
        "slug": args.slug,
        "manifest": str(path.relative_to(root)),
        "updated_at": now,
    })
    print(json.dumps(resolved_manifest(root, args.slug), ensure_ascii=False, indent=2))


def command_activate(args: argparse.Namespace) -> None:
    root = Path(args.root).expanduser().resolve()
    manifest = resolved_manifest(root, args.slug)
    path = manifest_path(root, args.slug)
    write_json(root / CURRENT_NAME, {
        "schema_version": 1,
        "slug": args.slug,
        "manifest": str(path.relative_to(root)),
        "updated_at": utc_now(),
    })
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


def current_slug(root: Path) -> str:
    current = load_json(root / CURRENT_NAME)
    slug = current.get("slug")
    if not isinstance(slug, str):
        raise ValueError("current-profile.json does not contain a valid slug")
    return slug


def command_resolve(args: argparse.Namespace) -> None:
    root = Path(args.root).expanduser().resolve()
    slug = args.slug or current_slug(root)
    print(json.dumps(resolved_manifest(root, slug, allow_draft=args.allow_draft), ensure_ascii=False, indent=2))


def command_list(args: argparse.Namespace) -> None:
    root = Path(args.root).expanduser().resolve()
    try:
        active = current_slug(root)
    except (FileNotFoundError, ValueError, json.JSONDecodeError):
        active = None
    result = []
    directory = root / "profiles"
    if directory.is_dir():
        for path in sorted(directory.glob(f"*/{MANIFEST_NAME}")):
            try:
                item = load_json(path)
            except (OSError, json.JSONDecodeError):
                continue
            result.append({
                "slug": item.get("slug"),
                "name": item.get("name"),
                "status": item.get("status"),
                "revision": item.get("revision"),
                "card_action": item.get("card_action") or LEGACY_CARD_ACTION,
                "active": item.get("slug") == active,
                "manifest_path": str(path.resolve()),
            })
    print(json.dumps(result, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage XHS IP card profiles")
    commands = parser.add_subparsers(dest="command", required=True)
    register = commands.add_parser("register")
    for name in ("root", "slug", "name", "action", "sheet", "clean-reference", "card-pose", "spec", "theme"):
        register.add_argument(f"--{name}", required=True)
    register.set_defaults(func=command_register)
    confirm = commands.add_parser("confirm")
    confirm.add_argument("--root", required=True); confirm.add_argument("--slug", required=True)
    confirm.set_defaults(func=command_confirm)
    activate = commands.add_parser("activate")
    activate.add_argument("--root", required=True); activate.add_argument("--slug", required=True)
    activate.set_defaults(func=command_activate)
    resolve = commands.add_parser("resolve")
    resolve.add_argument("--root", required=True); resolve.add_argument("--slug")
    resolve.add_argument("--allow-draft", action="store_true")
    resolve.set_defaults(func=command_resolve)
    listing = commands.add_parser("list")
    listing.add_argument("--root", required=True); listing.set_defaults(func=command_list)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        args.func(args)
    except (FileNotFoundError, ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
