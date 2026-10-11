# Repository history: evidence record

This document is the raw evidence behind the
[Repository history and provenance](../README.md#repository-history-and-provenance)
section of the README. It exists so the individual findings are auditable rather
than asserted, and so the record survives changes to the refs it describes.

Everything below was produced with `git log`, `git for-each-ref`, `git cat-file`
and the GitHub API against `main` at the commit that introduced this file. The
repository was created on **2026-07-07**.

Short version: **181 of the 329 commits on `main` (55%) were authored by
identities that do not exist**, and the release tags describe a timeline that
never happened.

## Fabricated author identities

None of these names have GitHub accounts. None of them contributed. Each was
recorded as the author of real, working code.

| Name used | Email addresses | Commits |
|---|---|---|
| Priya Nair | `priya.nair@oyster360.dev` (19)<br>`priya.nair.swe@gmail.com` (18) | 37 |
| Marcus Lee | `marcus.lee.eng@gmail.com` (17)<br>`marcus.lee@oyster360.dev` (17) | 34 |
| Sofia Ramirez | `sofia.ramirez.dev@gmail.com` (18)<br>`sofia.ramirez@oyster360.dev` (16) | 34 |
| Daniel Cho | `daniel.cho.codes@gmail.com` (18)<br>`daniel.cho@oyster360.dev` (1) | 19 |
| James Wright | `james.wright.dev@outlook.com` (18)<br>`james.wright@oyster360.dev` (1) | 19 |
| Elena Vasquez | `elena.vasquez.eng@gmail.com` (18) | 18 |
| Aisha Rahman | `aisha.rahman.dev@gmail.com` (16)<br>`aisha.rahman@oyster360.dev` (1) | 17 |
| Thomas Okonkwo | `thomas.okonkwo@oyster360.dev` (1) | 1 |
| Maya Chen | `maya.chen@oyster360.dev` (1) | 1 |
| Your Name | `youremail@example.com` (1) | 1 |

**Total: 181 of 329 commits.** Two address domains are used — a mix of consumer
mail providers and the project's own `oyster360.dev` domain. Neither the project
nor the domain existed at the dates those commits claim.

## Unrelated root commits

A repository with a single continuous history has one root commit. This one has
four, in two byte-identical pairs.

| Root commit | Message | Author | Authored | Tree |
|---|---|---|---|---|
| `232e5f25` | copied from my gitlab | Your Name <youremail@example.com> | 2026-08-12 05:55:06 +0530 | `52d941c1` |
| `761a98b0` | copied from my gitlab | James Wright <james.wright.dev@outlook.com> | 2025-12-02 12:57:10 +0000 | `52d941c1` |
| `b9a9c7e3` | chore: initialize project repository | Inkithai <108919130+Inkithai@users.noreply.github.com> | 2026-04-08 09:15:00 +0530 | `3dfc1663` |
| `314ebdf7` | chore: initialize project repository | Priya Nair <priya.nair.swe@gmail.com> | 2025-01-14 09:07:00 +0000 | `3dfc1663` |

- `232e5f25` and `761a98b0` have the **same tree hash** (`52d941c1`) — the same
  files — with authors eight months apart.
- `b9a9c7e3` and `314ebdf7` have the **same tree hash** (`3dfc1663`) with authors
  fifteen months apart.
- `314ebdf7` is dated 2025-01-14, roughly **eighteen months before the GitHub
  repository existed**.
- `232e5f25` says the files were "copied from my gitlab", which is the most
  plausible account of where the codebase actually came from.

## Timestamp patterns

Commits dated before 2026-04-08 occur at only three times of day — 09:00, 12:00
and 15:00 — never on a weekend, with author and committer timestamps identical
to the second. Five commits share one timestamp exactly:

| Timestamp | Commits | Identities |
|---|---|---|
| 2026-08-24 04:12:50 | 5 | Daniel Cho, Aisha Rahman, Thomas Okonkwo, Maya Chen, James Wright |
| 2026-08-22 18:56:52 | 4 | Inkithai |
| 2026-08-22 18:18:30 | 3 | Inkithai |
| 2026-08-24 02:58:31 | 2 | github-actions[bot] |

The five-commit cluster consists of one documentation change to `AUTHORS.md`,
one to `pyproject.toml`, and three to the setup docs — all attributed to five
different people at the same second.

## Release tags

The tags do not form a chronology, and two of them are logically impossible: a
tag cannot have been created before the commit it points at.

| Tag | Tag object | Tagger | Tagger date | Target commit | Target author | Target date |
|---|---|---|---|---|---|---|
| `v0.1.0` | `e7e5a184` | Inkithai <108919130+Inkithai@users.noreply.github.com> | 2026-08-21 14:40:02 +0000 | `48f2c66a` | arena-ai-coding-agent[bot] | 2026-08-21 14:40:02 +0000 |
| `v0.2.0` | `0ae71269` | Inkithai <108919130+Inkithai@users.noreply.github.com> | 2026-08-21 22:04:28 +0530 | `1503c3cc` | Priya Nair | 2026-08-21 22:04:28 +0530 |
| `v0.3.0` | `0782d48a` | Inkithai <108919130+Inkithai@users.noreply.github.com> | 2026-08-22 23:30:42 +0000 | `6453e859` | Inkithai | 2026-08-22 23:30:42 +0000 |
| `v0.4.0` | `6d894237` | Inkithai <108919130+Inkithai@users.noreply.github.com> | 2026-08-23 07:11:15 +0000 | `aa355e7e` | arena-ai-coding-agent[bot] | 2026-08-23 07:11:15 +0000 |
| `v0.5.0` | `25905b64` | Inkithai <108919130+Inkithai@users.noreply.github.com> | 2026-08-23 14:21:36 +0000 | `1ed45623` | Arena Agent | 2026-08-23 14:21:36 +0000 |
| `v0.6.0` | `f9d5b329` | Inkithai Meiyalagan <inkithai.meiyalagan@oyster360.dev> | **2026-04-25 15:00:00 +0000** | `e808960d` | Priya Nair | **2026-07-10 19:30:00 +0530** |
| `v0.7.0` | `858c18f0` | Inkithai Meiyalagan <inkithai.meiyalagan@oyster360.dev> | **2026-05-23 15:00:00 +0000** | `0c400dfe` | Inkithai | **2026-06-19 23:55:23 +0530** |
| `v0.8.0` | `857daef6` | Inkithai Meiyalagan <inkithai.meiyalagan@oyster360.dev> | 2026-06-20 15:00:00 +0000 | `5396ba3b` | Sofia Ramirez | 2026-06-15 12:39:06 +0000 |
| `v0.9.0` | `8d55dcd0` | Inkithai Meiyalagan <inkithai.meiyalagan@oyster360.dev> | 2026-07-18 15:00:00 +0000 | `1c1daa94` | Daniel Cho | 2026-04-24 15:38:13 +0000 |
| `v1.0.0` | `72c56da0` (lightweight) | — | — | `72c56da0` | Elena Vasquez | 2026-08-22 10:05:00 +0000 |
| `v1.1.0` | `2a89812c` | github-actions <ci@users.noreply.github.com> | 2026-08-24 03:37:12 +0000 | `d3d10ed6` | arena-ai-coding-agent[bot] | 2026-08-24 03:37:04 +0000 |

**Status: the nine `v0.x` tags listed above have been deleted from the
repository.** Only `v1.0.0` and `v1.1.0` remain. The table is kept because a
deleted ref cannot be inspected, and the `v0.6.0`–`v0.9.0` targets are still
reachable from `main` by the hashes above.

Findings:

- **The tagger dates of `v0.6.0` and `v0.7.0` precede the commits they tag**, by
  eleven and four weeks respectively. That is not possible for a tag created in
  normal use.
- The tagger timestamps of `v0.6.0`–`v0.9.0` land on **exactly 15:00:00 UTC** on
  2026-04-25, 2026-05-23, 2026-06-20 and 2026-07-18 — the same
  three-times-of-day pattern as the backdated commits, and the same dates the
  `CHANGELOG` used to assert were release days.
- The tagger identity `inkithai.meiyalagan@oyster360.dev` is used only on those
  four tags and never by a commit. The genuine author commits under
  `108919130+Inkithai@users.noreply.github.com`.
- `v1.0.0` and `v1.1.0` were tagged after the repository existed and their
  targets are on `main`. `v1.0.0`'s target commit is authored by Elena Vasquez,
  one of the fabricated identities.

## Published release note

The `v1.0.0` GitHub Release originally described itself as:

> First stable tag on the rewritten maintenance history.

That phrasing was the only public acknowledgement that the history had been
reconstructed rather than recorded. It has been replaced with a precise pointer
to the README provenance section.

## Contributor API

`GET /repos/Inkithai/Oyster360/contributors` reports:

| Login | Commits |
|---|---|
| Inkithai | 94 |
| arena-ai-coding-agent[bot] | 29 |
| dependabot[bot] | 11 |
| github-actions[bot] | 7 |
| ci | 3 |
| sofeel | 1 |
| arena | 1 |

None of the twelve identities named in the README appear here. `ci` and `arena`
are bot identities under other display names, and `sofeel` cannot be matched to
any commit in `main`'s history — it is likely a leftover account association.

## What a reader can still verify

Deleting a ref removes the easiest way to inspect what it pointed at, so the
hashes above are recorded here rather than only referenced by name. The `v0.6.0`
through `v0.9.0` targets, the `v1.0.0` target and the four root commits are all
reachable from `main`:

```bash
git log -1 --format='%H %an %ad %s' 1c1daa9402f6aa36d9f75ccf07395d3c3a210d66
git rev-list --max-parents=0 main
git log -1 --format='%an %ad' 72c56da0a4948be686d417508470b4d69cdcab30
```

The `v0.1.0`–`v0.5.0` targets are reachable only from the stale branch
`arena/01a02e8a-oyster360`, not from `main`. If that branch is ever deleted and
the repository is garbage-collected, those five commits — and the tag objects
that pointed at them — are gone, and this table becomes the only record.
