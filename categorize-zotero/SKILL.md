---
name: categorize-zotero
description: Classify Zotero papers into collections from final Obsidian literature notes, with optional approved cleanup of merged previews.
---

# Categorize Zotero

Classify Zotero inbox papers using their final Obsidian Zotero Integration notes. Propose one primary and zero or more secondary top-level collections per paper. Present a reviewable report before changing Zotero. Do not create tags.

## Configuration

Resolve each value from explicit user instructions in the current conversation, then the active project's loaded `AGENTS.md`. The latest explicit instruction wins. Resolve relative paths from `AGENTS.md` against the directory it governs. Do not read skill-local environment files or unrelated external configuration, or persist values without a request.

- Classification needs a source collection key or name, vault path, final article folder, and filename pattern (for example `@{citekey}.md`).
- Preview-readiness review additionally needs the preview folder, only when requested.
- Preview cleanup additionally needs the recoverable trash folder, only when requested. Resolve it before proposing exact moves for approval.

Do not guess folder conventions. Ask for missing values before the dependent operation and continue independent work when possible. Missing preview or trash settings must not block a classification-only request.

## Evidence and classification

Use the available Zotero skill/helper for access when needed. Read top-level items directly in the source collection, gathering only metadata needed for matching and updates: item key, title, citation key, creators, date, and collection keys.

Match each item to its final article note using the resolved filename pattern and actual citation key. Classify from the note's content, YAML `Category`/`category`, and summary/Category sections. Never substitute a preview note. If the final note is missing, report `Needs final article note`; do not reread PDFs or use title/abstract as a fallback unless the user explicitly requests that fallback.

- Use the central disease/research domain as primary. For methodological contributions, a method-oriented collection may be primary.
- Add secondary domains only when substantial to the paper's contribution or retrieval value, not merely because a common method is used.
- Use existing top-level collections when they fit; propose new ones when needed. Destinations are top-level; if the source is nested, clarify that scope before applying changes rather than treating its siblings as top-level.
- Do not infer subject matter from current collection membership, project names, prior filing habits, unrelated folder names, or Zotero tags. Collection names may identify destinations, not evidence about the paper.

## Report and approved changes

Read [references/report-format.md](references/report-format.md) when preparing the review report. Classification-only reports omit preview checks and paths. Keep missing-note and uncertain items visible with short evidence-based reasons.

Collection creation, destination addition, source removal, and preview cleanup are separate approval scopes, not necessarily separate questions. One explicit approval can cover clearly listed actions; retain that approval for the same unchanged proposal. If approval is ambiguous, perform only the clearly approved actions. Classification approval never implies preview cleanup approval.

After approval, create approved destinations, add items, and verify destination membership. Remove an item from the source only when removal is approved and its approved destinations are verified. Verify removal when performed. Retain the source membership and report failures when additions cannot be verified. Never edit Zotero's SQLite database directly; report unsupported writes instead.

Report created collections, updated items, items remaining in the source, missing notes, and failures/skips. Include cleanup results only when that mode was requested.

## Optional preview review and cleanup

Only when the user requests preview-readiness review or cleanup, read [references/preview-cleanup.md](references/preview-cleanup.md). Readiness review is read-only. Moving previews requires separate explicit approval and verified persistence of the summary in the final note, destination memberships, and absence from the source collection. Use recoverable moves only; never modify final article notes as cleanup.
