---
name: categorize-zotero
description: Classify Zotero inbox papers from final Obsidian literature notes and optionally clean up merged summary previews. Use when the user wants Codex to match Zotero citation keys to Obsidian @citekey article notes, review Category metadata, propose top-level collections, apply approved Zotero collection changes, or move successfully merged preview notes to an Obsidian trash folder after separate explicit approval.
---

# Categorize Zotero

## Overview

Use this skill to triage Zotero inbox papers from final Zotero Integration notes in Obsidian. Do not classify from the staging preview folder, and do not reread Zotero full text or PDFs when a matching final article note exists.

The skill classifies each paper into one primary top-level collection and zero or more secondary top-level collections. It writes a reviewable report first and applies Zotero changes only after explicit user approval.

This skill does not create tags. It does not use project names, previous filing habits, or current collection membership as classification evidence. A summary preview is a staging artifact only; move it to a recoverable trash folder only after its final article note and Zotero collection changes have been verified.

## Configuration

Resolve runtime values in this order:

1. Values explicitly provided in the current user request.
2. Values in the active project's loaded `AGENTS.md` instructions.

Current-request values override `AGENTS.md`. Do not read skill-local environment files or external configuration files. Do not persist values unless the user explicitly asks.

Interpret relative paths from `AGENTS.md` relative to the project directory governed by that file. Resolve each value independently. Before reading notes or changing Zotero, determine which values the requested operation needs. If any required value remains unresolved, stop and ask only for the missing values.

Required values depend on the operation:

- Categorization: source Zotero collection key or name, Obsidian vault path, final article folder, and filename pattern.
- Preview-readiness review: all categorization values plus the preview folder.
- Approved preview cleanup: all preview-readiness values plus the recoverable trash folder.

Do not assume conventional folders such as `library/articles`, `library/zotero-previews`, or `.trash/zotero-previews` when they are not specified by the current request or active `AGENTS.md`.

## Inputs

- Source Zotero collection: resolved collection key or name.
- Final Obsidian article folder: resolved vault path joined with the resolved final article folder.
- Note filename: resolved filename pattern, replacing `{citekey}` with the item's Zotero citation key.
- Preview staging folder: resolved vault path joined with the resolved preview folder.
- Recoverable preview destination: resolved vault path joined with the resolved trash folder.
- Separate user approval for Zotero writes, source-collection removal, and preview cleanup.

## Workflow

1. Invoke the Zotero skill if it is available, then check Zotero readiness with its helper.
2. Resolve the operation's required values from the current request and active `AGENTS.md`; ask only for missing values before continuing.
3. Read only top-level items directly inside the resolved Zotero collection.
4. For each Zotero item, gather only lightweight metadata needed to match notes: item key, title, citation key, creators, date, and current collection keys.
5. Build the expected Obsidian note path, such as `@{citekey}.md`.
6. Read the matching final Obsidian article note from the resolved final article folder; never substitute the preview note as classification evidence.
7. Classify from the final article content and its `Category` information.
8. Evaluate preview-cleanup readiness without moving anything: the final article must exist, contain a non-empty `# Summary` section and a `## Category` section, and the expected preview file must exist.
9. Write a categorization report for user review, including preview-cleanup readiness and exact source/destination paths.
10. Ask for explicit approval before applying changes. Treat collection creation, destination addition, source removal, and preview cleanup as separate decisions.
11. After approval, create approved collections, add items to approved destinations, and remove approved items from the source only when that removal was approved.
12. Verify each item's approved destination membership and removal from the source collection.
13. Only when all readiness checks pass, all approved destination additions succeed, source removal succeeds, and preview cleanup was explicitly approved, move the preview file to the resolved trash folder.

## Obsidian Note Rules

Prefer the final Obsidian article note over Zotero full text. The article note is assumed to contain the rendered Zotero highlights/notes plus the persisted summary imported from the preview.

Use these note sources when present:

- YAML frontmatter `Category` or `category`
- Markdown sections such as `Category`, `한줄 요약`, `핵심 주장`, `방법`, `주요 발견`, `한계`, and `읽기 전 체크포인트`
- Title and citation key in the note
- Any explicit domain, disease, data modality, study setting, or methodological focus described in the note

If a matching final article note is missing:

- Do not fall back to full text by default.
- Report the item as `Needs final article note`.
- Use Zotero title/abstract only if the user explicitly asks for a degraded fallback.

## Collection Rules

- Destination collections must be top-level collections at the same hierarchy level as the resolved source collection.
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

- current collection membership except for identifying the resolved input set
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
Read basis: final Obsidian article note | missing note | degraded metadata fallback
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
Preview note:
Preview cleanup readiness: Ready | Not ready
Proposed preview cleanup: Move <preview path> -> <trash path> | Keep
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

Treat collection creation, item collection updates, removal from the source collection, and preview cleanup as separate write actions. If approval is ambiguous, only perform the clearly approved actions. Approval to categorize or remove an item does not imply approval to move its preview.

Do not directly edit Zotero's SQLite database. If the available Zotero helper/local API cannot safely apply collection changes, stop and explain the write limitation instead of forcing a database edit.

After applying changes, summarize:

- created collections
- updated items
- items left in the source collection
- missing Obsidian notes
- preview notes moved to the recoverable trash folder
- preview notes retained, with the failed or unmet gate for each
- any failures or skipped items

## Preview Cleanup Safety

Preview cleanup is an optional finalization step, not part of classification itself.

- Resolve both preview and trash paths from the resolved vault plus the exact citation-key filename. Reject paths that escape the resolved folders.
- Require the final article note to contain a non-empty `# Summary` section and a `## Category` section. A transclusion/include statement alone is not proof that the summary was persisted.
- Require at least one approved destination addition to succeed and verify that the item is no longer directly in the resolved source collection.
- Require separate explicit approval for each proposed preview move, or an explicit approval covering all listed moves.
- Move the preview to the resolved trash folder; never permanently delete it and never delete or move a file under the resolved final article folder.
- Create the resolved trash folder only when an approved move is ready to run.
- Never overwrite an existing trash file. On a collision, retain the preview and report the destination collision.
- If the preview is already absent, report cleanup as skipped. If any note check or Zotero write/verification fails, retain the preview.

## Confidence Guidance

Use `High` when the Obsidian note has clear `Category` metadata and the summary strongly supports the destination collections.

Use `Medium` when the note supports the primary domain but secondary collections or destination naming could reasonably differ.

Use `Low` when the note is missing, incomplete, lacks category information, or spans multiple domains without a clear primary domain.
