---
name: export-md
description: Extract and summarize knowledge discussed in the current conversation into a Markdown file. Use when the user asks to export, save, capture, or preserve conceptual explanations, comparisons, definitions, principles, examples, procedures, or other reusable knowledge from the conversation as a .md file.
---

# Export MD

## Purpose

Create a Markdown knowledge note from the conversation. Focus on what the user learned or clarified, not on task management details.

For example, if the conversation discussed the difference between sRGB and RGB, the exported Markdown file should explain sRGB, RGB, their differences, use cases, and any examples or nuances covered in the conversation.

## Workflow

1. Identify the knowledge topic or topics discussed in the conversation.

2. Extract reusable knowledge:
   - Definitions and core concepts
   - Comparisons and distinctions
   - Principles, mechanisms, and reasoning
   - Examples, analogies, caveats, and edge cases
   - Practical usage guidance when it helps explain the topic
   - Relevant tags that describe the topic

3. Exclude task-management context unless it is directly needed to understand the knowledge:
   - Do not center the export on current progress, unfinished work, next tasks, blockers, or handoff status.
   - Do not include implementation plans, file paths, commands, or workflow notes unless they are part of the knowledge being documented.

4. Draft a concise Markdown knowledge note and show it to the user in chat before writing any file. Include YAML frontmatter properties at the top:
   - `date`: Use the current date in `YYYY-MM-DD` format.
   - `tags`: Use a short YAML list of topic tags inferred from the knowledge content.

5. Ask the user for approval to save the Markdown file. Do not create the file until the user clearly approves the draft.

6. If the user requests changes, revise the draft and ask for approval again.

7. After approval, save the Markdown file:
   - Use the path the user provides when one is specified.
   - If no path is specified, save it in the user's home directory using the actual absolute home path, such as `/Users/<username>/<filename>.md`.
   - Never use literal `~`, `~/`, `~.md`, or a relative `outputs/` path as the default save location.
   - If a user-provided path starts with `~/`, expand it to the actual absolute home path before writing.
   - Use a descriptive topic-based filename ending in `.md`.
   - Avoid overwriting an existing file unless the user explicitly approves replacement.
   - Write the approved Markdown directly to the final target path only.
   - Do not create or leave an additional copy in the current Codex workspace, `outputs/`, `work/`, or any temporary project directory.
   - If a temporary file is absolutely necessary for tooling, delete it before reporting completion.

8. If the Markdown note includes local images:
   - Save image files in an `images/` directory under the same directory that contains the Markdown file.
   - If the Markdown file is saved as `/Users/<username>/<topic-name>.md`, save images as `/Users/<username>/images/<topic-name>-image-1.png`, `/Users/<username>/images/<topic-name>-image-2.jpg`, and so on.
   - Reference images from the Markdown file using relative paths only, such as `![description](images/topic-name-image-1.png)`.
   - Do not store images in the current Codex workspace, `outputs/`, `work/`, or any temporary project directory.
   - If the image already exists at a stable web URL and the user wants to keep it remote, use that URL directly instead of downloading it.
   - Use the Markdown filename stem as the image filename prefix. Add a short descriptive suffix when useful, and preserve the original file extension when known.

9. Report only the final saved Markdown path after writing the file. Mention the `images/` directory only when local images were saved. Do not mention a workspace copy unless the user explicitly asked for one.

## Markdown Content

Use only sections that fit the topic. Prefer a knowledge-note structure such as:

```markdown
---
Date: YYYY-MM-DD
Tags:
  - tag-one
  - tag-two
---

# Topic Name

## Overview

## Key Concepts

## Comparison

## Examples

![short description](images/topic-name-image-1.png)

## Practical Notes

## Common Misunderstandings
```

Keep the export useful as a standalone reference. Preserve precise terminology, distinctions, and examples from the conversation, but avoid dumping the full transcript.
