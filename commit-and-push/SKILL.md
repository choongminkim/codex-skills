---
name: commit-and-push
description: Create task-focused Git commits and push when requested. Use for committing changes or organizing requested commits.
---

# Commit And Push

Create complete commits for the requested work while preserving unrelated user changes. Push only when the user's instructions authorize pushing; a request to organize or create commits alone does not authorize a push.

## Scope and commit grouping

Inspect the branch, working tree, staged changes, and relevant diffs. Determine the requested scope before staging. Treat already-staged changes as user work, not automatic permission to include them.

Each commit represents one logical, complete change. Include its implementation, regression tests, and necessary documentation together. Separate independent purposes, not file types. A rename and its updated references belong together when needed to keep the change complete.

Stage only the intended files or hunks and review the staged diff before each commit. Preserve unrelated changes and the user's staging state. If mixed edits cannot be separated safely, ask about that file while continuing independent work where possible.

## Commit messages

Use `category: Imperative description`, beginning the description with a base-form imperative verb.

| Category | Meaning |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `refactor` | Structural or implementation improvement without intended behavior changes |
| `chore` | Other standalone changes, including docs, formatting, tests, dependencies, configuration, and cleanup |

Choose the category for the commit's purpose, not each included file. For example, a fix with its regression test is `fix: Handle empty search results`. Add a concise body when the reason or validation needs explanation.

## Push and safety

- Do not revert, discard, or overwrite unrelated user work. Do not use destructive resets, file checkouts, or forced pushes without an explicit request and a clear understanding of the risk.
- Follow execution-environment permissions for staging, committing, and pushing. Do not request the same task approval again when authorization is already clear.
- Before an authorized push, verify the intended commits, remote, branch, upstream, and all commits that would be published, including pre-existing unpushed commits. Do not silently publish unrelated commits.
- Use `git push` for a clear tracking target, or `git push -u <remote> <branch>` when that upstream is clearly intended. Resolve an ambiguous destination before pushing. Report a rejected push without forcing it.

## Completion

Report created commit hashes and messages, relevant validation, and intentionally uncommitted changes. If pushed, state the branch, remote, and whether it succeeded. If the request was commit-only, report that completion without performing a push.
