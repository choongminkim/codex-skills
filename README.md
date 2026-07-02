# Codex Skills

Personal Codex skills managed as a Git repository.

## Sparse Checkout

To install only one skill from this repository, use Git sparse checkout:

```bash
git clone --filter=blob:none --sparse git@github.com:choongminkim/codex-skills.git ~/.codex/skills-temp
cd ~/.codex/skills-temp
git sparse-checkout set export-md
```

Then copy the selected skill directory into your active Codex skills directory:

```bash
mkdir -p ~/.codex/skills
cp -R export-md ~/.codex/skills/
```
