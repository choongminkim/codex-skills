---
name: summarize-zotero
description: Summarize papers directly from Zotero PDF attachments using full text plus metadata, abstracts, tags, and notes. Use when the user asks to summarize Zotero papers, scan a Zotero collection such as Unclassified, summarize a specific paper by title/citekey/Zotero key, compare papers, or create Markdown literature summaries from Zotero content.
---

# Summarize Zotero

Use this skill only for summarizing papers from Zotero.

## Default Inputs

- Config path: read from `.env` in this skill directory using `SUMMARIZE_ZOTERO_CONFIG`.
- Helper script: `scripts/summarize_zotero.py`
- Summary format reference: `references/summary-format.md`

The helper script must not hardcode a user-specific config path. When running commands that need config, prefer `--config <path>` if the user provided one; otherwise let the helper read `SUMMARIZE_ZOTERO_CONFIG` from `.env`. If `.env` is missing or does not define `SUMMARIZE_ZOTERO_CONFIG`, ask the user for the config path or initialize one before continuing.

Do not commit `.env`; it is ignored by `.gitignore` because it contains user-local paths.

## Workflow

1. Check Zotero access.
   - Use the Zotero helper or `scripts/summarize_zotero.py` to confirm the local API is available.
   - If Zotero API access fails, report the exact blocker.
2. Identify the target paper set.
   - For a collection request, use `zotero.collection_key` or `zotero.collection_name` from the config.
   - For a specific paper, match by title, citekey, Zotero item key, DOI, or author/title clue.
3. Gather source material.
   - Always collect title, authors, year, publication title, abstract, DOI/URL, Zotero item key, tags, and citekey when available.
   - Include Zotero notes/annotations only when available in metadata or rendered text provided by the user.
   - Always read the full text from Zotero PDF attachments before summarizing.
   - Do not make PDF full-text reading configurable in `zotero-obsidian.yaml`; it is the default purpose of this skill.
   - If no PDF attachment or indexed full text is available, report that blocker and only produce an abstract-based fallback if the user explicitly accepts that limitation.
4. Summarize.
   - Use the configured language, usually Korean.
   - Keep claims grounded in collected Zotero metadata, abstract, notes, annotations, and PDF full text.
   - Do not invent methods, results, datasets, numbers, or limitations that are not present in the source material.
   - Add a `Category` section with flat `prefix:value` keywords for downstream categorization.
   - Generate category keywords from the PDF full text; use Zotero tags only as source context.
   - Do not write generated category keywords to Zotero metadata.
5. Return the result.
   - By default, write a plain Markdown summary file after summarizing.
   - Use `obsidian.vault_path`, `obsidian.output_folder`, and `obsidian.filename_pattern` from the config to choose the destination.
   - The default filename pattern should be `@{citekey}`, producing names such as `@ZhangEtAl2026.md`.
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

Do not add title metadata blocks, DOI/Zotero link blocks, or `Source Metadata` sections unless the user explicitly asks. The saved Markdown file should contain only the configured summary sections and `Category`.

For a collection scan, produce one compact section per paper with title/citekey and a short reading-oriented summary.

## Safety

- Treat Zotero as the source of truth.
- Do not write to Zotero unless the user explicitly asks to add/import/update Zotero items or notes.
- Never write generated category keywords to Zotero item metadata.
- Preserve existing Zotero tags as source metadata only.
- Writing Markdown summaries to the configured Obsidian folder is allowed as the normal output for this skill.
- Do not patch or merge existing Zotero Integration notes unless the user explicitly asks for that behavior.

## References

Read `references/summary-format.md` when deciding section names or collection-summary format.
