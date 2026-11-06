<!-- @format -->

# Contributing

Thanks for your interest in contributing! This document explains the conventions this
repository expects, and why they exist, so your pull request passes CI and review on
the first try.

## Table of contents

- [Before you start](#before-you-start)
- [Repository purpose & rules](#repository-purpose--rules)
- [Branch naming](#branch-naming)
- [Commit messages](#commit-messages)
- [Pull requests](#pull-requests)
- [Automated checks (CI)](#automated-checks-ci)
- [Tests](#tests)
- [Code review & merging](#code-review--merging)

## Before you start

1. Fork or branch from `main`.
2. Install test dependencies:

    ```bash
    pip install -r requirements-test.txt
    ```

3. Make your changes, add or update tests, and run the test suite locally before
   opening a pull request (see [Tests](#tests)).

## Repository purpose & rules

This repository is **v2** of the API: Python, FastAPI, SQLAlchemy, PostgreSQL and a Redis
cache. It must match the v1 contract (`api-doc.yml` and the v1 regression tests) unless a
ticket says otherwise. Keep this in mind for every PR:

1. **v1 behavior is the default; every difference needs a ticket.** Do not copy v1 bugs. If
   a v1 regression test pinned a bug, update the test and name the ticket. Never weaken or
   skip a regression test only to make v2 pass.
2. **One ticket, one change.** Do not add unrequested features, and do not mix a refactor
   with a behavior change.
3. **Keep the contract in sync.** Update `api-doc.yml` in the same PR as the code. Put
   response models in `tests/integration/schemas.py`.
4. **Database changes go through migrations.** Never edit a merged migration. Never edit v1
   `data/*.json` files. Tests create their own data at runtime.
5. **Use the permission helper.** Go through `scripts/permission_users.py` (the
   `user_headers` fixture). Do not hardcode users or API keys, and do not skip tests for
   permission reasons.
6. **Keep test names unique per file.** `grep "^def test_" file.py | sort | uniq -d` must
   print nothing.
7. **Every endpoint has tests**, with the same categories for each resource.
8. **No dead code and no secrets.** Use environment variables and a `.env.example`.

The full rules are in [`AGENTS.md`](AGENTS.md) (general coding-agent instructions) and
[`.github/skills/code-review/SKILL.md`](.github/skills/code-review/SKILL.md) (GitHub Copilot
code review). Keep all three in sync.

## Branch naming

Branches must follow the `<type>/<short-description>` pattern, enforced automatically
by CI:

```
feat/add-login-page
fix/null-pointer-auth
docs/update-readme
```

- Allowed types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `tests`,
  `build`, `ci`, `chore`, `revert`, `dev`.
- The description may only contain lowercase letters, numbers, dots, underscores, and
  hyphens (`a-z0-9._-`).

## Commit messages

This project follows [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<optional scope>): <short description>
```

Examples:

```
feat: add login page
fix(auth): null pointer on expired token
docs: update README installation instructions
```

| Type             | Use for                                                     |
| ---------------- | ----------------------------------------------------------- |
| `feat`           | A new feature                                               |
| `fix`            | A bug fix                                                   |
| `docs`           | Documentation-only changes                                  |
| `style`          | Formatting only, no functional change (e.g. whitespace)     |
| `refactor`       | Code restructuring without changing behavior                |
| `perf`           | A performance improvement                                   |
| `test` / `tests` | Adding or updating tests                                    |
| `build`          | Changes to the build system or dependencies                 |
| `ci`             | Changes to CI/CD configuration (e.g. workflows themselves)  |
| `chore`          | Maintenance tasks with no impact on `src` or tests          |
| `revert`         | Reverting a previous commit                                 |
| `dev`            | Development-related changes that don't fit another category |

- Keep the description concise and written in the imperative mood ("add", not
  "added"/"adds").
- Do not end the subject line with a period.

## Pull requests

- **The PR title must also follow Conventional Commits** - it is validated
  automatically and the same rules as commit messages apply.
- The title must not end with a period.
- `WIP` PR titles are allowed, but signal the PR isn't ready to merge yet.
- Keep pull requests focused: one logical change per PR.
- Describe _why_ the change is needed, not just what changed.

## Automated checks (CI)

> **Note:** The workflows below exist in the v1 repository. They are not ported to v2 yet,
> so none of them run here until a ticket adds them.

Every push and pull request is meant to trigger the following GitHub Actions workflows. All of
them must pass before a PR can be merged.

| Workflow                   | Trigger                                          | What it checks                                                                        |
| -------------------------- | ------------------------------------------------ | ------------------------------------------------------------------------------------- |
| `pr-conventions.yml`       | PR opened / edited / synchronized                | PR title follows Conventional Commits, and branch name follows `<type>/<description>` |
| `pr-require-approvals.yml` | Review submitted / PR events                     | At least 2 approving reviews before merge                                             |
| `scan-secrets.yml`         | Push to `main` / every PR                        | TruffleHog scans for verified/leaked secrets (API keys, tokens, passwords)            |
| `tests.yml`                | Push to `main` / every PR                        | Installs dependencies and runs the full `pytest` suite                                |
| `test-parity.yml`          | Changes to test files or the parity check script | Every resource has the same categories of tests (no missing coverage)                 |

If a check fails, fix the underlying issue and push again - do not bypass checks.

If TruffleHog flags a secret, removing it from the current diff is not enough: rotate
(invalidate) the credential, since it may already be reachable from git history.

## Tests

Run the full test suite locally before opening a PR:

```bash
python -m pytest
```

If you add a new resource, make sure its test file covers the same test categories as
existing resources - see `scripts/check_test_parity.py`.

## Code review & merging

- A pull request needs **at least 2 approving reviews** before it can be merged.
  Only the latest review per reviewer counts; dismissed reviews do not.
- Address review feedback with additional commits rather than force-pushing, unless
  asked to clean up history before merge.
- Once approved and all checks are green, the PR can be merged.

---

**Quick checklist before opening a PR:**

- [ ] The PR links a ticket, and any difference from v1 behavior is named in it
- [ ] `api-doc.yml` is updated if endpoint behavior changed
- [ ] Database changes use a new migration (no edits to merged migrations)
- [ ] Test users were created via `permission_users.py` / `user_headers`, not by hand
- [ ] Test names are unique per file, and new endpoints have tests
- [ ] No dead code, no secrets committed
- [ ] Branch name follows `<type>/<description>`
- [ ] Commits (and PR title) follow Conventional Commits
- [ ] Tests passing locally
- [ ] PR description explains the _why_
