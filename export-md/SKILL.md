---
name: export-md
description: Save reusable knowledge from the current conversation as a Markdown note when the user requests an export.
---

# Export MD

Create a standalone knowledge note from what the conversation established: concepts, distinctions, reasoning, examples, caveats, and useful procedures. Exclude progress reports, blockers, handoff status, and incidental implementation details unless they are part of the knowledge the user wants to preserve.

## Draft and approval

- Draft a concise note with sections suited to the topic, rather than reproducing the transcript or forcing a fixed outline.
- Include YAML frontmatter with lowercase `date` (current date, `YYYY-MM-DD`) and `tags` (a short list inferred from the content).
- Show the complete draft in chat before saving and obtain approval for that draft. After requested revisions, present the revised draft for approval. Honor an already approved draft without asking again; explicit instructions to save directly override this default review step.

```markdown
---
date: YYYY-MM-DD
tags:
  - topic-tag
---

# Topic Name

Use only the explanations, comparisons, examples, and practical notes relevant to this topic.
```

## Save location

- Use the user's specified path. If omitted, save a descriptive `<topic-name>.md` in the actual absolute home directory. Expand a leading `~/`; never treat `~` as a literal filename or substitute a workspace/outputs folder as the default.
- Save only to the intended final location. A user-requested workspace or `outputs/` path is valid; do not create additional unsolicited copies. Remove any tooling-required temporary copy before reporting completion.
- Do not overwrite an existing file without explicit replacement approval.

## Images, when present

Save local images under `images/` beside the Markdown file. Prefix image filenames with the note's filename stem, add a descriptive suffix or number, and preserve the known extension. Use relative Markdown links such as `![description](images/topic-name-image-1.png)`.

Apply the same final-location and no-extra-copy rules to images. If the user wants an image to remain at a stable remote URL, link that URL instead of downloading it.

## Completion

Report the final saved Markdown path. Mention the adjacent `images/` directory only when local images were saved. Preserve precise terminology and distinctions so the note is useful without the conversation.
