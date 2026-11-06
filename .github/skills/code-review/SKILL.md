---
name: code-review
description: "Repository rules for reviewing pull requests in the v2 API repo. Use this whenever reviewing or commenting on a pull request or diff in this codebase."
---

<!-- @format -->

This repository is **v2** of the API (Python, FastAPI, SQLAlchemy, PostgreSQL, Redis cache).
It must match the v1 contract (`api-doc.yml` and the v1 regression tests) unless a ticket
says otherwise. Review every pull request against that purpose, and flag violations of the
following rules. The v1 rule "never change application behavior" does **not** apply here.

## 1. v1 behavior is the default; every difference needs a ticket

- Flag any change to routes, status codes, response shape or headers that no ticket or
  `api-doc.yml` entry backs.
- v1 bugs must not be copied. If a v1 ticket (labels `V1`, `bug`) describes the correct
  behavior, the diff should implement it and reference the ticket.
- A changed test expectation needs a named ticket. Reject any diff that weakens, deletes or
  skips a regression test only to make v2 pass.
- Reject any diff that edits the v1 repository or relies on v1 code.
- Find tickets with the `gh` CLI.

## 2. One ticket, one change

- Flag endpoints, fields or features that no ticket asks for.
- Flag PRs that mix a refactor with a behavior change.
- Flag unrelated "improvements" in files the PR touches.

## 3. The contract lives in one place

- A PR that changes endpoint behavior must update the API document in the same PR.
- Response models and validation schemas belong in the shared location (see `AGENTS.md`).
  Reject a new model defined inline in a test file or controller.
- Check that no model exists yet for that resource, including one in another open PR.

## 4. Database changes go through migrations

- Reject hand-made schema changes. Require a migration.
- Reject edits to a migration that was already merged.
- Reject any edit to `data/*.json` or any use of v1 JSON files as the source of truth.
- Tests must create their own data at runtime. They must not depend on hand-added rows.
- Redis is a cache only. Flag any change where a read can return stale data after a write.

## 5. Permission helper, no hand-crafted users

- Reject hardcoded API keys or user records in tests.
- Look for `user_headers(resource=..., method=..., allowed=...)`.
- Flag any `skip` whose reason is "no user has this permission". Ask for a real assertion,
  or `xfail` if the endpoint itself misbehaves.

## 6. Test function names must be unique within a file

Python keeps only the last definition when two functions in a module share a name. The
earlier test never runs, and its claimed coverage is false.

- Check the whole file, not only neighboring tests. Re-check after every rename.
- `grep "^def test_" file.py | sort | uniq -d` must print nothing. Treat any output as a bug.

## 7. Every endpoint has tests

- A new or changed endpoint needs tests in the same PR.
- Every resource covers the same test categories. `scripts/check_test_parity.py` must pass.
- Tests check what a client sees (status, body, headers), not internals.

## 8. Dead code

- Remove unused imports, variables, functions and files.
- Remove commented-out code and commented-out tests.
- Flag `TODO` markers without a ticket number.

## 9. Secrets

- Reject committed keys, tokens, passwords or connection strings. Only a `.env.example` with
  fake values is allowed.

## 10. Commits, branches and PRs

- Commit messages and the PR title follow Conventional Commits.
- The branch follows `<type>/<short-description>`.
- The PR links its ticket and explains why the change is needed.

## Additional things worth flagging

- **Shared-file collisions across concurrent PRs.** If a PR adds a class to a shared file
  (for example a model in `tests/integration/schemas.py`) and another open PR adds the same
  class, note it as a merge-coordination risk for whichever PR merges second.
- **Known v1 coupling in copied tests.** Do not approve new code that adds more coupling to
  `api/main.py`, `api/models/*.py`, `data/user.json` or `/api/v1/_test/reset-cache`.
