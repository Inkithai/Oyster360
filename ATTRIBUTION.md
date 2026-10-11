# Attribution

Who actually wrote Oyster360, and what cannot be established about it.

The Git history of this repository was removed and replaced with a single import
commit. Everything the old history asserted about authorship and dates had to be
reproduced here by hand or dropped, because there is nothing left in the
repository to read it from. The raw dump of the old history is kept outside the
repository by its owner — see [Keeping this honest](#keeping-this-honest).

## Who wrote the code

- **Inkithai Meiyalagan** ([@Inkithai](https://github.com/Inkithai)) — the
  application: backend platform, multi-tenancy and tenant isolation, data model,
  API, services, frontend, deployment and CI.

Automated tooling also appears in the removed history. None of these are people,
and none should be listed as a human contributor:

| Account | What it did |
|---|---|
| `arena-ai-coding-agent[bot]` | AI coding agent: test coverage, CI hardening, refactoring |
| `dependabot[bot]` | Dependency update pull requests |
| `github-actions[bot]` | Lockfile regeneration on Dependabot pull requests |
| `Arena Agent <agent@arena.ai>` | Early commits later replaced by the bot account above |

No other human has contributed a merged pull request or a commit under a
verifiable account. If that changes, add them above in the same pull request
that adds their work, as described in
[CONTRIBUTING.md](CONTRIBUTING.md).

## What cannot be established

**Nobody can say when any of this code was written.** The commits were copied
into this repository from a private GitLab, and the dates attached to them were
constructed rather than recorded. The distribution of work between individuals
is likewise unrecoverable: there is no source, no ticket, and no artifact that
says who wrote which line.

Nothing on this page should be read as a claim about chronology or about how the
work was divided. The only attribution that holds is the one above: one human
author, plus tooling.

## Names in the removed history that must never be credited

The removed history attributed 181 of its 329 commits to ten identities. **None of
them exist.** None has a GitHub account. None contributed. If you are reading a
citation, a contributor graph, a fork, or a cached page that credits any of the
names below, that source is repeating fabricated metadata.

| Name | Addresses used | Commits |
|---|---|---|
| Priya Nair | `priya.nair@oyster360.dev`, `priya.nair.swe@gmail.com` | 37 |
| Sofia Ramirez | `sofia.ramirez@oyster360.dev`, `sofia.ramirez.dev@gmail.com` | 34 |
| Marcus Lee | `marcus.lee@oyster360.dev`, `marcus.lee.eng@gmail.com` | 34 |
| Daniel Cho | `daniel.cho@oyster360.dev`, `daniel.cho.codes@gmail.com` | 19 |
| James Wright | `james.wright@oyster360.dev`, `james.wright.dev@outlook.com` | 19 |
| Elena Vasquez | `elena.vasquez.eng@gmail.com` | 18 |
| Aisha Rahman | `aisha.rahman@oyster360.dev`, `aisha.rahman.dev@gmail.com` | 17 |
| Thomas Okonkwo | `thomas.okonkwo@oyster360.dev` | 1 |
| Maya Chen | `maya.chen@oyster360.dev` | 1 |
| Your Name | `youremail@example.com` | 1 |

`Your Name` was a placeholder that was never replaced. It authored a root commit
whose message was "copied from my gitlab", which is the clearest single
explanation of where this codebase came from. The `oyster360.dev` domain in the
addresses above did not exist at the dates those commits claimed.

The ten names were also listed as maintainers in `AUTHORS.md` and
`pyproject.toml`. Those listings were removed.

## What those 181 commits actually changed

The table below is derived from the commit messages of the removed history, and
it is the only useful thing they still carry. **Read the left column as a label,
not a person.** The code changes are real; the names attached to them were
invented.

| Label in the removed history | Commits | Areas those commits touched |
|---|---|---|
| Priya Nair | 37 | models (9), backend (6), frontend (5), chore (4), test (4), api (2), services (2) |
| Marcus Lee | 34 | backend (6), services (5), models (5), frontend (4), api (4), test (2), ci (2) |
| Sofia Ramirez | 34 | frontend (6), services (6), docs (4), models (4), security (3), test (1) |
| Daniel Cho | 19 | chore (5), models (3), docs (2), frontend (2), backend (2), api (1) |
| James Wright | 19 | services (4), chore (2), deps (1), frontend (1), docs (1), db (1), test (1) |
| Elena Vasquez | 18 | services (7), chore (2), test (2), docs (1), api (1) |
| Aisha Rahman | 17 | models (4), docs (2), frontend (1), build (1), security (1), api (1) |
| Thomas Okonkwo | 1 | docs (1) |
| Maya Chen | 1 | docs (1) |
| Your Name | 1 | initial import |

Between them those commits cover the shell of the application: the SQLAlchemy
model layer, the service layer, the API routers, the Next.js frontend, the test
suites, and the deployment and CI scaffolding.

## Keeping this honest

The claim that the history was fabricated is only checkable against records that
survived it. Those records are:

- [`docs/history_provenance_evidence.md`](history_provenance_evidence.md) — the
  identities, addresses, commit counts, root commit hashes, timestamp
  collisions and the full tag table, captured from the history before it was
  removed.
- A backup bundle and a raw `git log --format=raw` dump of the old history,
  written by `scripts/rewrite_history.sh` before it changed anything and kept by
  the repository owner outside the repository.

If those are lost, this page becomes an unverifiable assertion, which is exactly
the failure it exists to correct. Keep them.

## If you are listed here and disagree

Open an issue. Attribution on this page is deliberately conservative: a name is
listed as a contributor only when a merged pull request or a commit under a
verifiable account exists to support it.
