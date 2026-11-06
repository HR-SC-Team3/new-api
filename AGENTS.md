# Agent instructions (v2)

These rules apply to any coding agent (AI or human-assisted) working in this repository -
whether writing code, reviewing a pull request, or editing a diff.

This is **v2** of the API. It replaces the v1 repository (`code`), which has its own
`AGENTS.md`. The v1 rules ("only document current behavior, never change the application")
do **not** apply here. In v2 the application code is the product, and you are expected to
change it.

## Purpose of this repository

The goal of this repository is to **build the new API on a new stack**, and to prove that it
matches the contract of v1 where that contract is correct.

- The v1 integration tests are the **regression suite**. They run over HTTP, so they can be
  run against v2 unchanged.
- The v1 `api-doc.yml` and the v1 tickets (label `V1`) are the **reference**. They describe
  the intended behavior and the known bugs.
- v2 does **not** reuse v1 code. v1 stores data in JSON files. v2 uses a different language,
  framework and database.

Judge every change against that purpose, and flag violations of the following rules.

## Stack

The team chose this stack (issue 147, "Do research"):

- Language: **Python**
- Framework: **FastAPI**
- ORM: **SQLAlchemy**
- Database: **PostgreSQL**, with **Redis** as cache
- Test runner: **pytest**, the same as v1

Rules:

- Do not add a language, framework, database or major dependency that is not in this list.
  If you need one, open a ticket first.
- Redis is a cache only. PostgreSQL is the single source of truth. A cache must never change
  what a client sees: after a write, the next read returns the new data.
- Rules below that name a tool or folder use the paths in "Project conventions".

## Rules

### 1. v1 behavior is the default; every difference needs a ticket

When v2 and v1 behave differently, the difference must be on purpose and written down.

- Match v1 behavior and the `api-doc.yml` contract (routes, status codes, response shape,
  headers) unless a ticket says otherwise.
- v1 bugs are **not** copied. If a v1 ticket (label `V1`, `bug`) describes the correct
  behavior, implement the correct behavior and reference that ticket.
- If a v1 regression test fails against v2, decide which side is wrong:
    - v2 is wrong -> fix v2.
    - The v1 test pinned a v1 bug or quirk -> update the test's expectation, and name the
      ticket that allows the change in the commit message or PR description.
- Never weaken, delete, skip or loosen a regression test only to make v2 pass. A change to
  an expectation must be justified by a ticket or by `api-doc.yml`.
- Do not edit the v1 repository from here, and do not edit v1 behavior. v1 is frozen
  reference material.
- Branches follow conventional commits. Find the right ticket with the `gh` CLI.

### 2. Scope: one ticket, one change

- Work from a ticket. Do not add endpoints, fields or features that no ticket asks for.
- Do not mix a refactor with a behavior change in one PR. Split them.
- Do not "improve" unrelated code while you are in the file.

### 3. The v2 contract lives in one place

- Keep the API documentation (OpenAPI or equivalent) in the repository and in sync with the
  code. A PR that changes an endpoint's behavior must update the documentation in the same PR.
- Keep response models and validation schemas in one shared location (see "Project
  conventions"). Do not define a new response model inline inside a test file or a controller.
- Before adding a model, check that none exists yet for that resource - including one added
  by another open PR.

### 4. Database changes go through migrations

- Never change the schema by hand or with ad hoc scripts. Add a migration.
- Never edit a migration that was already merged. Add a new one that fixes forward.
- Migrations must be reversible, or the PR must say why they cannot be.
- Do not edit the v1 JSON files (`data/*.json`) or copy them in as the source of truth. If you
  need seed data, put it in a seed script or fixture owned by v2.
- Tests create the data they need at runtime (through the API, a factory or a fixture). They
  never depend on rows that someone added by hand.

### 5. Use the permission helper, don't hand-craft users

Tests that need a user with specific permissions must go through one shared permission helper
that creates a user on demand for a `(resource, method, allowed)` combination.

- Never hardcode API keys or user records in a test.
- Do not add permission-test users to seed data to get a test to pass.
- Do not skip a test because "no user has that permission". Generate one. Prefer running the
  test (or marking it `xfail` if the endpoint itself misbehaves) over skipping it for a
  permission reason.

### 6. Test function names must be unique within a file

A duplicate name in the same module can silently replace the earlier test in some languages
and runners. The earlier test then never runs, and its coverage claim becomes false.

- When you add or rename a test, check the whole file for name collisions, not just
  neighboring tests. A rename can create a new collision.
- Run a duplicate-name check before you push (for Python: `grep "^def test_" file.py | sort | uniq -d`
  must print nothing). Add the equivalent for the chosen stack to "Project conventions".

### 7. Every endpoint has tests, and every resource has the same categories

- A new or changed endpoint ships with tests in the same PR.
- Each resource covers the same categories of tests (success, not found, malformed id,
  validation error, permission denied, and so on). Keep the parity check script (or its
  replacement) up to date and passing.
- Test the behavior that a client sees (status code, body, headers), not the internals.

### 8. Remove dead code before merging

- Remove unused imports, variables, functions and files.
- Remove commented-out code and commented-out tests. Finish them or delete them.
- Do not leave `TODO` markers without a ticket number.

### 9. No secrets in the repository

- Never commit keys, tokens, passwords or connection strings. Read them from environment
  variables. Commit only an example file (for example `.env.example`) with fake values.
- If a secret is committed, removing it from the diff is not enough. Rotate it.

### 10. Commits, branches and PRs follow the project convention

- Commits and PR titles follow Conventional Commits. Branches use `<type>/<short-description>`.
- Keep PRs small and focused. Explain why the change is needed, and link the ticket.
- A PR needs the required approvals and green CI before merge. Do not bypass checks.

## Project conventions

| Item                         | Value                                                                |
| ---------------------------- | -------------------------------------------------------------------- |
| Language / framework         | Python / FastAPI                                                     |
| Database / migration tool    | PostgreSQL + Redis cache / Alembic (assumed, confirm before use)     |
| Test runner and command      | `python -m pytest` (config in `pytest.ini`)                          |
| Location of shared schemas   | `tests/integration/schemas.py` (copied from v1)                      |
| Permission helper            | `scripts/permission_users.py` + `user_headers` fixture (copied)      |
| Parity check script          | `scripts/check_test_parity.py` (copied)                              |
| Duplicate test-name check    | `grep "^def test_" file.py \| sort \| uniq -d`                       |
| Location of the API document | `api-doc.yml` (copied from v1, update it as v2 changes)              |
| Location of the v1 reference | The `code` repository (frozen) and its tickets labeled `V1`          |

## Known v1 coupling in the copied tests

The tests were copied from v1 without edits. They do not run against v2 yet. Remove each
coupling in a ticketed PR, and keep the test assertions the same:

- `tests/integration/conftest.py` starts `api/main.py` as a subprocess and probes port 3000.
  v2 needs its own server start (for example uvicorn) or a base URL from an environment
  variable.
- `conftest.py` reads and writes `data/user.json` to create permission users, and uses
  `preserve_data_files` and the `/api/v1/_test/reset-cache` endpoint. v2 has no JSON data
  files. Rewrite the helper to create users in PostgreSQL (or through the API).
- Several `test_*.py` files read `api/models/*.py` at import time (`*_MODEL_SOURCE`). These
  are v1 source files, so collection fails. Remove them (see rule 8).
- `requirements-test.txt` includes `requirements.txt`, which does not exist yet in v2.

Rules 4 and 5 apply to the rewrite: no `data/` files, and no hand-made users.

## Where else these rules live

Keep these files in sync with this one:

- `CONTRIBUTING.md` - human contributor guide.
- `.github/skills/code-review/SKILL.md` - GitHub Copilot code review agent skill.

The v1 CI workflows (`.github/workflows/`) are not ported yet. Add them with a ticket.
