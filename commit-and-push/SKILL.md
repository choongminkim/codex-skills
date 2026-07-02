---
name: commit-and-push
description: Use when the user asks Codex to commit and push git changes, save current work to a remote repository, create separate commits for multiple tasks, or prepare disciplined git history. Guides Codex to inspect the worktree, group related changes into isolated complete commits, write category-prefixed imperative commit messages, and push safely without including unrelated user changes.
---

# Commit And Push

## Overview

Create clean, task-focused git commits and push them to the configured remote. Preserve unrelated user work, use explicit commit message categories, and report exactly what was committed and pushed.

## Workflow

1. Inspect the repository state with `git status --short --branch`.
2. Review relevant changes with `git diff`, `git diff --staged`, and file-level inspection as needed.
3. Separate changes into logical commit groups by task, behavior, or intent.
4. Stage only the files or hunks for the first complete group.
5. Commit with a valid message.
6. Repeat staging and committing until all requested changes are committed.
7. Confirm the current branch and remote tracking state.
8. Push with `git push`, or `git push -u <remote> <branch>` only when upstream is clearly intended from repository context.

## Commit Message Rules

Every commit message must start with one of these categories:

- `feat`: Add a new feature.
- `fix`: Fix a bug.
- `refactor`: Change code for readability, maintainability, performance, or convenience without changing intended behavior.
- `chore`: Everything else, including documentation, formatting, tests, dependency updates, configuration, cleanup, and removing dead code.

Use this format:

```text
category: Imperative description
```

The description must start with a base-form imperative verb and describe what the commit does.

Good examples:

```text
feat: Add user profile settings
fix: Handle empty search results
refactor: Simplify registration flow
chore: Add API integration tests
```

When a commit needs detail, add a blank line and a concise body:

```text
refactor: Rewrite user registration logic in Rust

Improve registration throughput by moving validation into the Rust service.
Tested on Rust v1.66.
```

## Commit Grouping

Each commit should contain one isolated, complete change. Prefer several small commits over one mixed commit when changes have different purposes.

Use separate commits for examples like:

- Renaming variables or files.
- Adding or updating tests.
- Fixing a specific bug.
- Adding a feature.
- Updating documentation or formatting.

Avoid:

- Mixing refactors, features, tests, and documentation in one commit when they can stand alone.
- Spreading one logical change across multiple commits.
- Staging unrelated files because they are present in the worktree.

## Safety Rules

- Do not revert, discard, or overwrite user changes unless explicitly requested.
- Leave unrelated changes unstaged.
- If a file contains both related and unrelated edits, use partial staging when practical.
- If partial staging is ambiguous or risky, ask before committing that file.
- Do not run destructive commands such as `git reset --hard`, `git checkout -- <file>`, or forced pushes unless the user explicitly asks and the risk is clear.
- Use escalation or approval when the execution environment requires it for `git add`, `git commit`, or `git push`.
- Push only after verifying that the intended commits exist and the branch target is clear.

## Final Response

After pushing, tell the user:

- The branch and remote that were pushed.
- Each commit hash and commit message.
- Whether the push succeeded.
- Any changes intentionally left uncommitted.
