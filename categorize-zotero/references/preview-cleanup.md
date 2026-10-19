# Preview review and cleanup

This optional workflow applies only when requested. Review is read-only; cleanup requires approval covering the exact moves. Classification or source-removal approval does not imply cleanup approval.

## Readiness review

Resolve the vault, final article folder, preview folder, actual citation key, and filename pattern. Use the matching final article note as evidence that the preview has been merged.

- The final note must contain a non-empty `# Summary` section and a `## Category` section. A transclusion/include alone is not proof that the summary was persisted.
- Confirm the expected preview exists. Missing files or incomplete notes are not ready; explain the missing condition.
- For review alone, do not require a trash folder, create folders, or move files.

## Approved moves

Before proposing moves, resolve the recoverable trash folder and exact source/destination filenames. Then obtain explicit approval for selected moves or all listed moves. An existing approval remains valid for the unchanged list; do not ask again merely because the workflow reached its write step.

For each move:

- Resolve paths, including symlinks, and reject paths escaping the specified preview/trash folders. Never move a final article note or use a destination under the final article folder.
- Recheck that the final note contains the persisted summary and Category, and the preview still exists.
- Require at least one approved destination membership and verify all approved destination additions. Verify that the item is no longer directly in the source collection. Source removal itself must have been approved. For resumed cleanup, verified results of previously approved changes count; do not repeat additions solely to qualify.
- If any note check, required Zotero change, or verification fails, retain the preview and report the unmet gate.
- Create the trash directory only when an approved move is ready. Move to recoverable trash; never permanently delete or overwrite an existing trash file. On collision, retain the preview.
- Verify the preview is at the destination and absent from its old path. If already absent before the move, report skipped rather than claiming success.

Report previews moved, retained, and skipped, with reasons for unmet gates or failures. Do not alter final article notes during cleanup.
