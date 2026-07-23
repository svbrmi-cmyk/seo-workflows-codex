# Workspace persistence

- Store all user-created project artifacts under `D:\CODEX`. Do not place or duplicate
  custom skills, reports, scripts, source files, or generated deliverables on `C:`.
- Keep reusable project skills under `D:\CODEX\.agents\skills`, with their canonical
  source stored elsewhere under `D:\CODEX` when appropriate.
- Use `https://github.com/svbrmi-cmyk/seo-workflows-codex` as the canonical GitHub
  repository for this workspace.
- Publish only reusable skills and their supporting source files to
  `svbrmi-cmyk/seo-workflows-codex`. Do not publish generated reports, edited texts,
  research results, customer inputs, or other task outputs to GitHub.
- Keep generated results under `D:\CODEX` only unless the user explicitly names another
  destination.
- After completing changes to a skill, commit and push only the intended skill changes.
  Inspect scope first and never include unrelated files.
- If Git, GitHub CLI authentication, a valid repository, or a configured remote is
  unavailable, preserve the completed work on `D:\CODEX` and report the exact GitHub
  publication blocker instead of inventing a destination.
- System applications and their managed runtime files are outside this artifact-storage
  rule unless the user explicitly asks to relocate or uninstall them.

