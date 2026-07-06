#!/usr/bin/env python3
"""Utilities for the summarize-zotero skill."""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


BASE_URL = "http://127.0.0.1:23119/api/users/0"
API_HEADERS = {"Zotero-API-Version": "3"}
SKILL_DIR = Path(__file__).resolve().parents[1]
ENV_FILE = SKILL_DIR / ".env"
CONFIG_ENV_KEY = "SUMMARIZE_ZOTERO_CONFIG"


CONFIG_TEMPLATE_TEXT = """zotero:
  collection_name: ""
  collection_key: ""
  include_subcollections: true

obsidian:
  vault_path: ""
  output_folder: ""
  filename_pattern: "@{citekey}"

summary:
  language: "ko"
  sections:
    - "한줄 요약"
    - "핵심 주장"
    - "방법"
    - "주요 발견"
    - "한계"
    - "내 연구와의 관련성"
    - "인용할 만한 포인트"
"""


def fail(message: str, code: int = 1) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(code)


def load_dotenv(path: Path = ENV_FILE) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            values[key] = value
    return values


def resolve_config_path(raw_config: str | None) -> Path:
    if raw_config:
        return Path(raw_config).expanduser()
    env = load_dotenv()
    config = env.get(CONFIG_ENV_KEY)
    if config:
        return Path(config).expanduser()
    fail(
        f"Config path not provided. Pass --config or set {CONFIG_ENV_KEY}=... in {ENV_FILE}"
    )


def scalar(value: str) -> Any:
    value = value.strip()
    if value in {"true", "false"}:
        return value == "true"
    if value in {"null", "~"}:
        return None
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def minimal_yaml(text: str) -> dict[str, Any]:
    root: dict[str, Any] = {}
    stack: list[tuple[int, Any]] = [(-1, root)]
    last_key_for_indent: dict[int, tuple[Any, str]] = {}

    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        line = raw.strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]

        if line.startswith("- "):
            item = scalar(line[2:])
            if not isinstance(parent, list):
                fail("Unsupported YAML list placement in config")
            parent.append(item)
            continue

        if ":" not in line:
            continue
        key, raw_value = line.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()

        if raw_value:
            parent[key] = scalar(raw_value)
            last_key_for_indent[indent] = (parent, key)
            continue

        child: dict[str, Any] = {}
        parent[key] = child
        last_key_for_indent[indent] = (parent, key)
        stack.append((indent, child))

        # Convert child mapping into a list if the next non-empty child line is a list.
        # The simple parser handles this lazily in a second pass below.

    # Repair known list fields from the simple parse.
    def collect_list(section: str, key: str) -> None:
        pattern = re.compile(rf"^\s{{4}}{re.escape(key)}:\s*$\n((?:\s{{6}}- .+\n?)+)", re.M)
        match = pattern.search(text)
        if not match:
            return
        values = [scalar(line.strip()[2:]) for line in match.group(1).splitlines()]
        if section in root and isinstance(root[section], dict):
            root[section][key] = values

    collect_list("summary", "sections")
    if "note" in root and isinstance(root["note"], dict):
        fm = root["note"].get("frontmatter")
        if isinstance(fm, dict):
            pattern = re.compile(r"^\s{4}tags:\s*$\n((?:\s{6}- .+\n?)+)", re.M)
            match = pattern.search(text)
            if match:
                fm["tags"] = [scalar(line.strip()[2:]) for line in match.group(1).splitlines()]
    return root


def load_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        fail(f"Config not found: {path}")
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        loaded = yaml.safe_load(text)
        if not isinstance(loaded, dict):
            fail("Config root must be a mapping")
        return loaded
    except ModuleNotFoundError:
        return minimal_yaml(text)


def api_get(path: str) -> tuple[Any, dict[str, str]]:
    url = f"{BASE_URL}{path}"
    request = urllib.request.Request(url, headers=API_HEADERS)
    with urllib.request.urlopen(request, timeout=20) as response:
        body = response.read().decode("utf-8")
        headers = dict(response.headers.items())
    return json.loads(body), headers


def all_pages(path: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    start = 0
    limit = 100
    sep = "&" if "?" in path else "?"
    while True:
        page, _headers = api_get(f"{path}{sep}limit={limit}&start={start}")
        if not isinstance(page, list):
            fail(f"Expected list response from Zotero for {path}")
        rows.extend(page)
        if len(page) < limit:
            return rows
        start += limit


def creator_names(data: dict[str, Any]) -> list[str]:
    names: list[str] = []
    for creator in data.get("creators") or []:
        if "name" in creator:
            names.append(creator["name"])
        else:
            name = " ".join(part for part in [creator.get("firstName"), creator.get("lastName")] if part)
            if name:
                names.append(name)
    return names


def year_from_date(raw: str | None) -> str:
    if not raw:
        return ""
    match = re.search(r"\d{4}", raw)
    return match.group(0) if match else ""


def bibtex_key(bibtex: str | None) -> str:
    if not bibtex:
        return ""
    match = re.search(r"@\w+\s*\{\s*([^,\s]+)", bibtex)
    return match.group(1) if match else ""


def fallback_citekey(data: dict[str, Any]) -> str:
    creators = data.get("creators") or []
    surname = ""
    if creators:
        first = creators[0]
        surname = first.get("lastName") or first.get("name") or ""
    surname = re.sub(r"[^A-Za-z0-9]+", "", surname) or "Unknown"
    year = year_from_date(data.get("date"))
    return f"{surname}{year}" if year else surname


def safe_filename(name: str) -> str:
    return re.sub(r'[\\/:*?"<>|]+', "-", name).strip()


def obsidian_config(config: dict[str, Any]) -> dict[str, Any]:
    obsidian = config.get("obsidian") or {}
    if not isinstance(obsidian, dict):
        fail("Config obsidian section must be a mapping")
    return obsidian


def filename_pattern_from_config(config: dict[str, Any]) -> str:
    pattern = obsidian_config(config).get("filename_pattern") or "@{citekey}"
    return pattern.replace("{zotero-key}", "{zotero_key}")


def output_dir_from_config(config: dict[str, Any]) -> Path:
    obsidian = obsidian_config(config)
    vault_path = obsidian.get("vault_path")
    output_folder = obsidian.get("output_folder")
    if not vault_path:
        fail("Set obsidian.vault_path")
    if not output_folder:
        fail("Set obsidian.output_folder")
    return Path(vault_path).expanduser() / output_folder


def item_children(item_key: str) -> list[dict[str, Any]]:
    encoded = urllib.parse.quote(item_key)
    return all_pages(f"/items/{encoded}/children?format=json")


def attachment_fulltext(attachment_key: str) -> dict[str, Any]:
    encoded = urllib.parse.quote(attachment_key)
    try:
        data, _headers = api_get(f"/items/{encoded}/fulltext")
    except Exception as exc:
        return {
            "attachment_key": attachment_key,
            "content": "",
            "chars": 0,
            "error": str(exc),
        }
    content = data.get("content", "") if isinstance(data, dict) else str(data)
    return {
        "attachment_key": attachment_key,
        "content": content,
        "chars": len(content),
        "indexed_pages": data.get("indexedPages") if isinstance(data, dict) else None,
        "total_pages": data.get("totalPages") if isinstance(data, dict) else None,
    }


def pdf_fulltexts(item_key: str) -> list[dict[str, Any]]:
    texts: list[dict[str, Any]] = []
    for child in item_children(item_key):
        data = child.get("data", child)
        if data.get("itemType") != "attachment":
            continue
        content_type = data.get("contentType") or ""
        title = data.get("title") or ""
        if "pdf" not in content_type.lower() and ".pdf" not in title.lower():
            continue
        attachment_key = child.get("key") or data.get("key") or ""
        if not attachment_key:
            continue
        fulltext = attachment_fulltext(attachment_key)
        fulltext["title"] = title
        fulltext["content_type"] = content_type
        texts.append(fulltext)
    return texts


def summarize_item(item: dict[str, Any], filename_pattern: str) -> dict[str, Any]:
    data = item.get("data", item)
    citekey = bibtex_key(item.get("bibtex")) or fallback_citekey(data)
    year = year_from_date(data.get("date"))
    title = data.get("title") or "Untitled"
    filename = filename_pattern.format(
        citekey=citekey,
        year=year,
        title=safe_filename(title),
        zotero_key=item.get("key") or data.get("key") or "",
    )
    if not filename.endswith(".md"):
        filename += ".md"
    return {
        "title": title,
        "authors": creator_names(data),
        "year": year,
        "citekey": citekey,
        "zotero_key": item.get("key") or data.get("key") or "",
        "item_type": data.get("itemType") or "",
        "publication_title": data.get("publicationTitle") or data.get("conferenceName") or "",
        "abstract": data.get("abstractNote") or "",
        "doi": data.get("DOI") or "",
        "url": data.get("url") or "",
        "tags": [tag.get("tag") for tag in data.get("tags") or [] if tag.get("tag")],
        "note_filename": safe_filename(filename),
        "zotero_select": f"zotero://select/library/items/{item.get('key') or data.get('key') or ''}",
    }


def cmd_init_config(args: argparse.Namespace) -> None:
    path = resolve_config_path(args.config)
    if path.exists() and not args.force:
        fail(f"Config already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(CONFIG_TEMPLATE_TEXT, encoding="utf-8")
    print(path)


def cmd_validate_config(args: argparse.Namespace) -> None:
    path = resolve_config_path(args.config)
    config = load_config(path)
    errors: list[str] = []
    zotero = config.get("zotero") or {}
    obsidian = config.get("obsidian") or {}
    summary = config.get("summary") or {}
    if not (zotero.get("collection_key") or zotero.get("collection_name")):
        errors.append("Set zotero.collection_key or zotero.collection_name")
    if not obsidian.get("vault_path"):
        errors.append("Set obsidian.vault_path")
    if not obsidian.get("output_folder"):
        errors.append("Set obsidian.output_folder")
    if summary and not summary.get("language"):
        errors.append("Set summary.language")
    if errors:
        print(json.dumps({"ok": False, "errors": errors}, ensure_ascii=False, indent=2))
        raise SystemExit(2)
    print(json.dumps({"ok": True, "config": str(path)}, ensure_ascii=False, indent=2))


def cmd_collections(_args: argparse.Namespace) -> None:
    rows = all_pages("/collections?format=json")
    for row in rows:
        data = row.get("data", row)
        key = row.get("key") or data.get("key")
        name = data.get("name") or ""
        parent = data.get("parentCollection")
        suffix = f" parent={parent}" if parent else ""
        print(f"{key}   {name}{suffix}")


def collection_key_from_config(config: dict[str, Any]) -> str:
    zotero = config.get("zotero") or {}
    if zotero.get("collection_key"):
        return zotero["collection_key"]
    target = zotero.get("collection_name")
    if not target:
        fail("Config must include zotero.collection_key or zotero.collection_name")
    matches = []
    for row in all_pages("/collections?format=json"):
        data = row.get("data", row)
        if data.get("name") == target:
            matches.append(row.get("key") or data.get("key"))
    if not matches:
        fail(f"No Zotero collection named {target!r}")
    if len(matches) > 1:
        fail(f"Multiple Zotero collections named {target!r}; set collection_key instead")
    return matches[0]


def cmd_export_items(args: argparse.Namespace) -> None:
    config = load_config(resolve_config_path(args.config))
    key = collection_key_from_config(config)
    pattern = filename_pattern_from_config(config)
    encoded = urllib.parse.quote(key)
    rows = all_pages(f"/collections/{encoded}/items/top?include=data,bibtex&format=json")
    items = []
    for row in rows:
        summary = summarize_item(row, pattern)
        if args.include_fulltext:
            summary["pdf_fulltexts"] = pdf_fulltexts(summary["zotero_key"])
        items.append(summary)
    payload = {
        "collection_key": key,
        "output_dir": str(output_dir_from_config(config)),
        "count": len(items),
        "items": items,
    }
    if args.out:
        out = Path(args.out).expanduser()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(out)
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    subcommands = parser.add_subparsers(required=True)

    init_config = subcommands.add_parser("init-config")
    init_config.add_argument("--config")
    init_config.add_argument("--force", action="store_true")
    init_config.set_defaults(func=cmd_init_config)

    validate = subcommands.add_parser("validate-config")
    validate.add_argument("--config")
    validate.set_defaults(func=cmd_validate_config)

    collections = subcommands.add_parser("collections")
    collections.set_defaults(func=cmd_collections)

    export_items = subcommands.add_parser("export-items")
    export_items.add_argument("--config")
    export_items.add_argument("--out")
    export_items.add_argument(
        "--no-fulltext",
        action="store_false",
        dest="include_fulltext",
        help="Skip Zotero PDF attachment full text export",
    )
    export_items.set_defaults(include_fulltext=True)
    export_items.set_defaults(func=cmd_export_items)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
