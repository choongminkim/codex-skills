# Summary Format

Use these sections for Korean paper summaries unless the user asks for another structure.

## Single Paper

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
- evidence:...
- setting:...
- data:...
- population:...
- outcome:...
- metric:...
```

## Category Rules

- Use `## Category`, not `## AI Classification`.
- Place `## Category` as the final section in saved Markdown files.
- Use a flat bullet list of `prefix:value` keywords only.
- Do not add heading 3 subsections under `Category`.
- Use lowercase prefixes: `domain`, `task`, `method`, `evidence`, `setting`, `data`, `population`, `outcome`, `metric`, `score`.
- Use lowercase kebab-case values by default, such as `risk-stratification` or `machine-learning`.
- Preserve conventional uppercase acronyms or proper names when clearer, such as `EHR`, `AUROC`, `ICU`, `ED`, `SOFA`, `LLM`, `CT`, and `MRI`.
- Keep equivalent concepts to one spelling within a project, such as always using `data:EHR` instead of mixing `data:EHR` and `data:ehr`.
- Generate 5-12 category keywords grounded in PDF full text.
- Do not write category keywords to Zotero metadata.

## Collection Scan

Use one compact section per paper:

```markdown
## @citekey - Short Title

- 한줄 요약: ...
- 왜 읽을까: ...
- 확인할 포인트: ...
```

## Style Rules

- Write in Korean unless configured otherwise.
- Preserve English technical terms when clearer.
- Keep the summary factual and source-grounded.
- Use PDF full text as the default source. If only abstract-level information is available, label that as a blocker or explicit fallback.
- Do not claim full-paper details unless full text or user-provided notes support them.
- Do not add extra title metadata blocks, DOI/Zotero link blocks, or `Source Metadata` sections unless explicitly requested.
