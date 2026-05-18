# Contributing to MedWatch (Backend)

This document describes the team workflow for contributing to the MedWatch backend repository. MedWatch is the Proyek 1 Pengembangan Perangkat Lunak Desktop submission by Kelompok B5, D4 Teknik Informatika, Politeknik Negeri Bandung, semester 2 TA 2025/2026.

## Team and module ownership

Each member owns exactly one anggota module. Files under `anggotaN/` are READ-ONLY for non-owners. Integration adjustments that would touch a teammate's file must be implemented as a wrapper or adapter under `api/` or `integrasi/`. New additive files under a teammate's folder (for example, `anggota3/NewestVisualization/`) are allowed and attributed to the corresponding owner. See `CLAUDE.md` Rule 2 for the full policy.

| Owner | NIM | Role | Module | GitHub |
|---|---|---|---|---|
| Ghaisan Khoirul Badruzaman | 251524048 | Project Leader | anggota1 (scraping plus openFDA acquisition) | Finerium |
| Bimo Surya Anggara | 251524040 | Quality Assurance | anggota2 (CRUD pasien SOAP) | Bisura16 |
| Alia Ardani | 251524035 | System Analyst | anggota3 (visualisasi matplotlib) | vssixla |
| Muhammad Iqbal | 251524057 | Programmer | anggota4 (drug safety check) | BallVoldigoad |
| Abhidal Muhammad Gazza | 251524032 | UI/UX Designer | anggota5 (PDF export plus auth) | Heimdall |

Shared layers `api/`, `integrasi/`, `docs/`, `ProductionGrade-ImplementationPlan/`, and the top-level config files are co-owned and maintained by Ghaisan as Project Leader on behalf of the team.

## Conventional Commits (required)

Every commit message uses the Conventional Commits specification (https://www.conventionalcommits.org). Allowed types:

- `feat:` a new feature.
- `fix:` a bug fix.
- `docs:` documentation only.
- `chore:` tooling, configuration, repository hygiene.
- `refactor:` code change that neither fixes a bug nor adds a feature.
- `test:` adding or correcting tests.
- `perf:` performance improvement.

Optional scope in parentheses describes the area of the change, for example `fix(safety): include active medications in interaction check`. The body explains what changed and why, never how. No `Co-authored-by` Claude trailer. No emoji. No em dashes.

## Branch model

- `main` is the default integration branch. Only Project Leader merges to `main`.
- Per-anggota feature branches follow the pattern `<github-handle>_anggotaN` (for example `Abhidal_anggota5`).
- Cross-cutting integration branches follow the pattern `ghaisan-<topic>` (for example `ghaisan-APIIntegration`).
- Long-running feature work rebases onto `main` before opening a pull request to avoid bulky merge commits.

## Code review

Every pull request requires at least one peer approval before merge. The Project Leader self-merges via `gh pr merge --squash` after recording the reviewer in the PR body. Reviewers check:

- Acceptance criteria from the originating ticket are satisfied.
- Tests pass locally (`api/tests/smoke_test.py` for backend changes).
- No teammate file under `anggotaN/` is modified without owner authorization.
- No credential VALUES are present anywhere in the diff (resource NAMES are allowed).
- Conventional commit subject is correct.

## Language conventions

- User-facing strings (UI labels, error messages, log messages displayed to humans, documentation prose) are written in Bahasa Indonesia with formal register.
- Code identifiers (variable names, function names, class names, file names) are written in English.
- Standards citations (OWASP Top 10, GCP IAM roles, HTTP method names, RFC references) are written in English.
- Date formatting in displayed content uses `dd-MM-yyyy` (Indonesian convention). Date formatting in JSON storage uses ISO 8601 (`YYYY-MM-DDTHH:MM:SSZ`).
- Money values render with the Rupiah symbol when displayed.

## Local development

1. Clone the repository and create a Python virtual environment: `python3 -m venv .venv && source .venv/bin/activate`.
2. Install dependencies: `pip install -r api/requirements.txt`.
3. Copy `.env.example` to `.env` and fill in your local values (see `.env.example` comments for guidance).
4. Run the backend: `JWT_SECRET=$(cat .env | grep JWT_SECRET | cut -d= -f2) PORT=8080 .venv/bin/python -m api.app`.
5. Smoke test in a second terminal: `JWT_SECRET=dev-mission-secret-local-2026 PORT=8080 CORS_ORIGINS=http://localhost:3000 .venv/bin/python api/tests/smoke_test.py`. Expected output: `done all smoke tests passed` (14/14).

## Security

- Never commit credential VALUES. Use placeholders in `.env.example`. Real secrets live in GCP Secret Manager.
- The pre-commit secret-scan hook (`.claude/scripts/secret-scan.sh`) blocks commits whose staged diff matches forbidden patterns (API keys, GitHub tokens, AWS keys, Slack tokens, private keys, JWT_SECRET with a real value, service-account JSON, embedded URL credentials).
- Report security issues to the Project Leader privately rather than opening a public issue.

## Question or doubt

Open an issue with the prefix `question:` or contact the Project Leader. Do not block on ambiguity: log the question, proceed with the conservative interpretation, and surface it during the next sync.
