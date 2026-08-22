---
name: summarize-zotero
description: Summarize papers directly from Zotero PDF attachments using full text plus metadata, abstracts, tags, and notes. Use when the user asks to summarize Zotero papers, scan a Zotero collection such as Unclassified, summarize a specific paper by title/citekey/Zotero key, compare papers, or create Markdown literature summaries from Zotero content.
---

# Summarize Zotero

Use this skill only for summarizing papers from Zotero.

## Project Configuration

Resolve runtime values in this order:

1. Values explicitly provided in the current user request.
2. Values in the active project's loaded `AGENTS.md` instructions.

Current-request values override `AGENTS.md`. Do not read skill-local environment files or external configuration files. Do not persist values unless the user explicitly asks.

Interpret relative paths from `AGENTS.md` relative to the project directory governed by that file. Before accessing Zotero or writing a summary, list the values required for the requested operation and resolve each one independently. If any required value remains unresolved, stop and ask only for the missing values.

Required values depend on the operation:

- Collection scan: Zotero collection key or collection name.
- Saved Markdown output: Obsidian vault path, output folder, and filename pattern.
- Chat-only output: no Obsidian destination values.
- Specific-paper request: a paper identifier supplied by the request or discoverable through Zotero; a collection value is not required.

The skill writes Korean summaries unless the current request specifies another language.

## Helper

- Script: `scripts/summarize_zotero.py`
- Summary format reference: `references/summary-format.md`

The skill interprets the current request and active `AGENTS.md`, then passes resolved values directly to the helper. For a collection export, use the applicable arguments:

```bash
python3 scripts/summarize_zotero.py export-items \
  --collection-key <key> \
  --vault-path <vault> \
  --output-folder <folder> \
  --filename-pattern '<pattern>'
```

Use `--collection-name` instead of `--collection-key` when only the name is available. Do not invoke the helper until all arguments required by that command have been resolved.

## Workflow

1. Check Zotero access.
   - Use the Zotero helper or `scripts/summarize_zotero.py` to confirm the local API is available.
   - If Zotero API access fails, report the exact blocker.
2. Identify the target paper set.
   - For a collection request, use the resolved collection key or collection name.
   - For a specific paper, match by title, citekey, Zotero item key, DOI, or author/title clue.
3. Gather source material.
   - Always collect title, authors, year, publication title, abstract, DOI/URL, Zotero item key, tags, and citekey when available.
   - Include Zotero notes/annotations only when available in metadata or rendered text provided by the user.
   - Always read the full text from Zotero PDF attachments before summarizing.
   - PDF full-text reading is the default purpose of this skill and is not a project routing option.
   - If no PDF attachment or indexed full text is available, report that blocker and only produce an abstract-based fallback if the user explicitly accepts that limitation.
4. Summarize.
   - Write in Korean by default unless the user explicitly asks for another language.
   - Keep claims grounded in collected Zotero metadata, abstract, notes, annotations, and PDF full text.
   - Do not invent methods, results, datasets, numbers, or limitations that are not present in the source material.
   - Add a `Category` section with flat `prefix:value` keywords for downstream categorization.
   - Generate category keywords from the PDF full text; use Zotero tags only as source context.
   - Do not write generated category keywords to Zotero metadata.
5. Return the result.
   - By default, write a plain Markdown summary file after summarizing.
   - Use the resolved Obsidian vault path, output folder, and filename pattern to choose the destination.
   - A filename pattern such as `@{citekey}` produces names such as `@ZhangEtAl2026.md`.
   - Also provide a brief chat confirmation with the saved path and a compact summary.
   - If the user explicitly asks for chat-only output, do not write a file.

## Output Shape

For a single paper, prefer:

```markdown
## 한줄 요약

...

## 핵심 주장

...

## 방법

...

## 주요 발견

...

## 한계

...

## 인용할 만한 포인트

...

## 읽기 전 체크포인트

- ...

## Category

- domain:...
- task:...
- method:...
- evidence:...
- setting:...
- data:...
- population:...
- outcome:...
- metric:...
```

`Category` must be the final section in saved Markdown files. It must be a flat list only. Do not add heading 3 subsections under `Category`. Use lowercase prefixes. Use lowercase kebab-case values by default, but preserve conventional uppercase acronyms or proper names such as `EHR`, `AUROC`, `ICU`, `ED`, `SOFA`, `LLM`, `CT`, and `MRI`. Keep equivalent concepts to one spelling within a project.

Do not add title metadata blocks, DOI/Zotero link blocks, or `Source Metadata` sections unless the user explicitly asks. The saved Markdown file should contain only the skill-defined summary sections and `Category`.

For a collection scan, produce one compact section per paper with title/citekey and a short reading-oriented summary.

## Safety

- Treat Zotero as the source of truth.
- Do not write to Zotero unless the user explicitly asks to add/import/update Zotero items or notes.
- Never write generated category keywords to Zotero item metadata.
- Preserve existing Zotero tags as source metadata only.
- Writing Markdown summaries to the resolved Obsidian folder is allowed as the normal output for this skill.
- Do not patch or merge existing Zotero Integration notes unless the user explicitly asks for that behavior.

## References

Read `references/summary-format.md` when deciding section names or collection-summary format.
