---
name: summarize-zotero
description: Summarize or compare Zotero papers from PDF full text, with Markdown literature notes as the default output.
---

# Summarize Zotero

Summarize papers held in Zotero. Read PDF full text and write Korean summaries unless the user requests another language. Preserve the distinction between source findings and interpretation.

## Configuration and scope

Resolve each runtime value from explicit user instructions in the current conversation, then the active project's loaded `AGENTS.md`. The latest explicit instruction wins. Interpret relative paths from `AGENTS.md` relative to the directory it governs. Do not read skill-local environment files or unrelated external configuration, or persist values without a request.

- Collection work needs a collection key or name; a specific paper needs an identifier such as title, citekey, item key, or DOI, supplied by the user or discoverable through Zotero.
- Saving individual notes needs the vault path, output folder, and filename pattern. Do not guess these values.
- Chat-only output needs no Obsidian destination. Missing save settings do not block identifying papers or reading source material; ask for missing values before the dependent save step.

## Source and output requirements

- Gather available title, authors, year, publication, abstract, DOI/URL, item key, tags, and citation key. Use notes/annotations when available in metadata or user-provided rendered text.
- Read the PDF attachment full text before summarizing. Check reported indexing coverage; incomplete or unavailable text is a blocker for a full-paper summary, not permission to infer missing results. Use an abstract-only fallback only when the user explicitly accepts it. Report affected papers and continue with independent papers when possible.
- Ground methods, results, numbers, limitations, and Category keywords in source material. Zotero tags provide context, not generated classification labels.
- Before drafting, read [references/summary-format.md](references/summary-format.md) for the applicable output mode and Category rules. Keep the format defined there rather than duplicating it here.
- By default, save one Markdown summary per paper to the resolved destination and report the saved paths with a compact chat summary. For chat-only output, write no files. A collection reading overview is a separate compact output mode; it does not replace the individual-note format when saving literature summaries.

## Access and helper routing

Use available Zotero read tools to identify papers and retrieve attachments. Report access failures accurately. The bundled helper exports source material as JSON; it does not generate or save Markdown summaries.

Read [references/helper-usage.md](references/helper-usage.md) when using `scripts/summarize_zotero.py`, including collection source-only reads and destination planning. For a specific paper, use Zotero item lookup and full-text access; the helper's collection command does not require selecting an unrelated collection.

## Identity and writes

- Do not invent an author/year citation key. Distinguish exported BibTeX keys from missing keys, and verify the key used by Zotero Integration before relying on an `@citekey` filename for downstream matching. Resolve a missing key or obtain an explicit item-key naming choice before saving.
- Check proposed filenames for collisions and existing files before writing. Do not silently replace an existing note or treat two items as the same paper because their filenames match.
- Do not modify Zotero items or notes without an explicit request. Never write generated Category keywords to Zotero metadata; preserve existing tags.
- Saving Markdown to the resolved destination is normal output. Do not patch or merge existing Zotero Integration notes unless explicitly requested.
