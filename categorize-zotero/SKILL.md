---
name: categorize-zotero
description: Classify Zotero inbox papers into one or more top-level domain collections using existing Obsidian summary notes instead of rereading full text. Use when the user wants Codex to read Zotero items from a configured collection, match Zotero citation keys to Obsidian @citekey markdown files, review note content and Category metadata, create a categorization report, propose existing or new top-level collections, and apply Zotero collection changes only after explicit approval.
---

# Categorize Zotero

## Overview

Use this skill to triage Zotero inbox papers by reusing existing Obsidian summaries. Do not reread Zotero full text or PDFs for classification when a matching Obsidian note exists.

The skill classifies each paper into one primary top-level collection and zero or more secondary top-level collections. It writes a reviewable report first and applies Zotero changes only after explicit user approval.

This skill does not create tags. It does not use project names, previous filing habits, or current collection membership as classification evidence.

## Configuration

Read configuration from a `.env` file in the same folder as this `SKILL.md`.

The `.env` file must define only the config path needed by this skill:

```dotenv
CATEGORIZE_ZOTERO_CONFIG=/absolute/path/to/zotero-obsidian.yaml
```

`CATEGORIZE_ZOTERO_CONFIG` must point to a YAML config with this shape:

```yaml
zotero:
  collection_name: "Unclassified"
  collection_key: "5UKV2FYM"

obsidian:
  vault_path: "/path/to/Obsidian Vault"
  output_folder: "library/zotero-previews"
  filename_pattern: "@{citekey}"
```

If `.env` is missing, do not guess paths or fall back to other environment variable names. Tell the user to create it next to `SKILL.md`:

```dotenv
CATEGORIZE_ZOTERO_CONFIG=/absolute/path/to/zotero-obsidian.yaml
```

If the YAML config is missing required fields, stop and report the missing keys.

## Inputs

- Source Zotero collection: `zotero.collection_key` from the config.
- Obsidian note folder: `obsidian.vault_path` joined with `obsidian.output_folder`.
- Note filename: `obsidian.filename_pattern`, replacing `{citekey}` with the item's Zotero citation key.
- User approval before any Zotero write action.

## Workflow

1. Invoke the Zotero skill if it is available, then check Zotero readiness with its helper.
2. Load `.env` from the skill folder and parse the YAML config it points to.
3. Read only top-level items directly inside the configured Zotero collection.
4. For each Zotero item, gather only lightweight metadata needed to match notes: item key, title, citation key, creators, date, and current collection keys.
5. Build the expected Obsidian note path, such as `@{citekey}.md`.
6. Read the matching Obsidian markdown note.
7. Classify from the markdown note content and its `Category` information.
8. Write a categorization report for user review.
9. Ask for explicit approval before applying changes.
10. After approval, create any approved top-level collections that do not exist, add items to approved destination collections, and remove approved items from the source collection only if the user approved that cleanup.

## Obsidian Note Rules

Prefer Obsidian note evidence over Zotero full text. The summary note is assumed to be the already-processed representation of the paper.

Use these note sources when present:

- YAML frontmatter `Category` or `category`
- Markdown sections such as `Category`, `한줄 요약`, `핵심 주장`, `방법`, `주요 발견`, `한계`, and `읽기 전 체크포인트`
- Title and citation key in the note
- Any explicit domain, disease, data modality, study setting, or methodological focus described in the note

If a matching note is missing:

- Do not fall back to full text by default.
- Report the item as `Needs summary note`.
- Use Zotero title/abstract only if the user explicitly asks for a degraded fallback.

## Collection Rules

- Destination collections must be top-level collections at the same hierarchy level as the configured source collection.
- Use existing top-level collections when the name already matches the recommended domain.
- Propose a new top-level collection when no existing top-level collection fits.
- Allow one primary collection plus zero or more secondary collections for a paper.
- Use the primary collection for the paper's central research domain.
- Use secondary collections only when the paper substantially belongs to another domain, not merely because it uses a common method.
- Keep method-oriented collections for papers whose main contribution is methodological rather than domain-applied.

## Classification Rules

Base classification on the Obsidian note's content and `Category` metadata:

- primary disease or research domain
- data modality or domain when central to the paper
- clinical/research setting when it is a major retrieval axis
- method domain only when method development or evaluation is central
- summary claims and stated contribution

Do not use these as classification evidence:

- current collection membership except for identifying the configured input set
- project names
- folder names outside the destination top-level collection names
- previous user filing habits
- Zotero tags as a source of truth

When a paper combines a domain and a method, prefer the domain as primary. For example, a machine learning model for sepsis prediction should use `Sepsis` as primary, with `Medical AI`, `Time Series`, or another secondary collection only if the Obsidian note shows that domain is substantial enough for future retrieval.

## Report Format

Write the report before making changes. Include one entry per item:

```text
Title:
Zotero item key:
Citation key:
Obsidian note:
Read basis: Obsidian summary note | missing note | degraded metadata fallback
Note Category:
Primary collection:
Secondary collections:
New collections needed:
Confidence: High | Medium | Low
Reason:
- ...
Alternative considered:
- ...
Proposed Zotero changes:
- Create top-level collection ... (if needed)
- Add item to ...
- Remove item from source collection: yes/no
Needs user decision:
- ...
```

Keep reasons short and evidence-based. Paraphrase note evidence; do not quote long passages.

## Approval And Write Safety

Never modify Zotero during the report phase.

Before applying changes, ask the user to approve either:

- all recommendations,
- selected item-level recommendations, or
- a revised set of destinations.

Treat collection creation, item collection updates, and removal from the source collection as separate write actions. If approval is ambiguous, only perform the clearly approved actions.

Do not directly edit Zotero's SQLite database. If the available Zotero helper/local API cannot safely apply collection changes, stop and explain the write limitation instead of forcing a database edit.

After applying changes, summarize:

- created collections
- updated items
- items left in the source collection
- missing Obsidian notes
- any failures or skipped items

## Confidence Guidance

Use `High` when the Obsidian note has clear `Category` metadata and the summary strongly supports the destination collections.

Use `Medium` when the note supports the primary domain but secondary collections or destination naming could reasonably differ.

Use `Low` when the note is missing, incomplete, lacks category information, or spans multiple domains without a clear primary domain.
