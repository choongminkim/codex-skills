#!/usr/bin/env python3
"""Utilities for the summarize-zotero skill."""

from __future__ import annotations

import argparse
import json
import re
import sys
from string import Formatter
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


BASE_URL = "http://127.0.0.1:23119/api/users/0"
API_HEADERS = {"Zotero-API-Version": "3"}
def fail(message: str, code: int = 1) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(code)


def runtime_config_from_args(args: argparse.Namespace) -> dict[str, Any]:
    missing: list[str] = []
    if not (args.collection_key or args.collection_name):
        missing.append("collection_key or collection_name")
    source_only = getattr(args, "source_only", False)
    if not source_only:
        for name in ("vault_path", "output_folder", "filename_pattern"):
            if not getattr(args, name, None):
                missing.append(name)
    if missing:
        raise ValueError("Missing required values: " + ", ".join(missing))

    return {
        "zotero": {
            "collection_key": args.collection_key,
            "collection_name": args.collection_name,
        },
        "source_only": source_only,
        "obsidian": {} if source_only else {
            "vault_path": args.vault_path,
            "output_folder": args.output_folder,
            "filename_pattern": args.filename_pattern,
        },
    }


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


def summarize_item(item: dict[str, Any], filename_pattern: str | None) -> dict[str, Any]:
    data = item.get("data", item)
    citekey = bibtex_key(item.get("bibtex"))
    item_key = item.get("key") or data.get("key") or ""
    year = year_from_date(data.get("date"))
    title = data.get("title") or "Untitled"
    filename = None
    filename_error = None
    if filename_pattern is not None:
        fields = {field for _, field, _, _ in Formatter().parse(filename_pattern) if field}
        if "citekey" in fields and not citekey:
            filename_error = "Missing citation key required by filename pattern"
        elif "zotero_key" in fields and not item_key:
            filename_error = "Missing Zotero item key required by filename pattern"
        else:
            filename = filename_pattern.format(
                citekey=citekey, year=year, title=safe_filename(title), zotero_key=item_key,
            )
            if not filename.endswith(".md"):
                filename += ".md"
            filename = safe_filename(filename)
    return {
        "title": title,
        "authors": creator_names(data),
        "year": year,
        "citekey": citekey,
        "citekey_source": "bibtex" if citekey else "missing",
        "zotero_key": item.get("key") or data.get("key") or "",
        "item_type": data.get("itemType") or "",
        "publication_title": data.get("publicationTitle") or data.get("conferenceName") or "",
        "abstract": data.get("abstractNote") or "",
        "doi": data.get("DOI") or "",
        "url": data.get("url") or "",
        "tags": [tag.get("tag") for tag in data.get("tags") or [] if tag.get("tag")],
        "note_filename": filename,
        "filename_error": filename_error,
        "zotero_select": f"zotero://select/library/items/{item.get('key') or data.get('key') or ''}",
    }


def flag_filename_collisions(items: list[dict[str, Any]]) -> None:
    by_name: dict[str, list[dict[str, Any]]] = {}
    for item in items:
        name = item["note_filename"]
        if name:
            by_name.setdefault(name.casefold(), []).append(item)
    for group in by_name.values():
        if len(group) > 1:
            for item in group:
                item["filename_error"] = f"Filename collision: {item['note_filename']}"
                item["note_filename"] = None


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
    try:
        config = runtime_config_from_args(args)
    except ValueError as exc:
        fail(str(exc))
    key = collection_key_from_config(config)
    pattern = None if config["source_only"] else filename_pattern_from_config(config)
    encoded = urllib.parse.quote(key)
    rows = all_pages(f"/collections/{encoded}/items/top?include=data,bibtex&format=json")
    items = []
    for row in rows:
        summary = summarize_item(row, pattern)
        if args.include_fulltext:
            summary["pdf_fulltexts"] = pdf_fulltexts(summary["zotero_key"])
        items.append(summary)
    flag_filename_collisions(items)
    payload = {
        "collection_key": key,
        "output_dir": None if config["source_only"] else str(output_dir_from_config(config)),
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

    collections = subcommands.add_parser("collections")
    collections.set_defaults(func=cmd_collections)

    export_items = subcommands.add_parser("export-items")
    export_items.add_argument("--collection-key")
    export_items.add_argument("--collection-name")
    export_items.add_argument("--vault-path")
    export_items.add_argument("--output-folder")
    export_items.add_argument("--filename-pattern")
    export_items.add_argument("--out")
    export_items.add_argument(
        "--source-only", action="store_true",
        help="Fetch source material without planning Markdown destinations or filenames",
    )
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
