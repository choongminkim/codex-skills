# Helper usage

`../scripts/summarize_zotero.py` reads Zotero's local API and emits JSON source material. Resolve the script relative to this skill, not the user's project. It does not write Markdown notes or mutate Zotero.

## Source-only collection retrieval

When only fetching material, or before save settings are known:

```bash
python3 <skill-dir>/scripts/summarize_zotero.py export-items \
  --collection-key <key> --source-only
```

Use `--collection-name <name>` instead when needed. No vault, output folder, or filename pattern is required in source-only mode. The payload has no planned note destination or filename.

## Retrieval with note destination planning

When the three save settings have been resolved:

```bash
python3 <skill-dir>/scripts/summarize_zotero.py export-items \
  --collection-key <key> \
  --vault-path '<vault>' \
  --output-folder '<folder>' \
  --filename-pattern '@{citekey}'
```

This adds destination and filename proposals to the JSON. The agent still writes the summaries separately. Existing destination-planning calls keep requiring all three save settings.

## Commands and fields

- `collections` lists available collections and can check API access.
- Full text is included by default. `--no-fulltext` is for metadata inspection; its output is insufficient for the default full-paper summary.
- `--out <path>` saves the JSON payload instead of printing it, including in source-only mode. It is not a Markdown output option. Use only an intended export path and check an existing file before replacing it.
- `citekey_source` distinguishes an exported `bibtex` key from `missing`; an exported key is not a guarantee that an external citation-key plugin uses the same key.
- A missing key is left empty rather than replaced with an invented author/year key. A pattern requiring `{citekey}` then produces no `note_filename` and explains the blocker in `filename_error`. An explicit `{zotero_key}` pattern can be used when the user has chosen it.
- Batch filename collisions are reported for all affected items, with no filename proposed. Resolve them before writing notes. Check existing destination files separately.
- Inspect full-text errors and `indexed_pages`/`total_pages`; non-empty indexed text alone does not establish complete PDF coverage.
