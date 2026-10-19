# Summary Format

Read this before drafting. Write in Korean by default, retain useful English technical terms, and follow an explicitly requested alternative language or structure.

## Individual literature notes

Use this format for a single saved paper and for each paper saved during a collection task:

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
```

The saved note contains the summary sections and Category only. Do not add title metadata, DOI/Zotero link blocks, or a Source Metadata section unless requested. Report missing evidence rather than inventing content to fill a section.

## Category rules

- Put `## Category` last in each saved literature note. Use a flat list of `prefix:value` keywords, with no heading 3 subsections.
- Use lowercase prefixes such as `domain`, `task`, `method`, `evidence`, `setting`, `data`, `population`, `outcome`, `metric`, and `score`.
- Prefer 5–12 relevant keywords when the full text supports them; do not pad the list or require every prefix.
- Use lowercase kebab-case values, preserving conventional uppercase acronyms or proper names such as `EHR`, `AUROC`, `ICU`, `ED`, `SOFA`, `LLM`, `CT`, and `MRI`. Use consistent spellings within the project.
- Generate keywords from PDF full text. For an explicitly accepted abstract-only fallback, label the limited basis and restrict keywords to that evidence. Do not write generated keywords to Zotero metadata.

## Collection reading overview

Use this compact format when the user requests a collection overview, or as a chat companion to individually saved notes:

```markdown
## @citekey - Short Title

- 한줄 요약: ...
- 왜 읽을까: ...
- 확인할 포인트: ...
```

Use the Zotero item key when a citation key is unavailable, clearly identifying it as an item key. Do not present it as a citation key. This overview does not require per-paper Category lists and is not the format for saved individual literature notes.

If the user requests saving the overview itself, use the requested output path or ask for the missing destination. Do not require an individual-note filename pattern for a single overview file.

## Comparisons and evidence

For a comparison, use shared dimensions relevant to the request, such as research question, method, data, findings, and limitations. Save individual literature notes only when requested or when the task also includes the default per-paper summaries; resolve a destination separately for a requested comparison file.

Keep all outputs source-grounded. Identify an explicitly accepted partial or abstract-based fallback so it cannot be mistaken for a full-paper summary.
