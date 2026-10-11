# Rewriting the repository history

How to remove fabricated authorship and dates from the Git history.

**The governing rule: write nothing that is not true.** Every field this
procedure writes — author, committer, date, message — is a fact. Where a fact is
unknowable, it is left unknown and said to be unknown, rather than filled with
something plausible.

Evidence for everything below is in
[history_provenance_evidence.md](history_provenance_evidence.md). The reasoning
is in the [README](../README.md#repository-history-and-provenance).

## The problem, stated precisely

Of **329 commits** on `main`, **213 carry metadata that cannot be true**:

| Category | Commits | What is wrong |
|---|---|---|
| Fabricated author + date before the repository existed | 146 | Name never existed; date predates repo creation |
| Real author + date before the repository existed | 30 | Owner's name on a date that cannot be real |
| Fabricated author + plausible date | 34 | Name never existed |
| Real author + plausible date | 116 | Nothing wrong |
| Timestamps pinned to 09:00:00 / 12:00:00 / 15:00:00 | 3 | Constructed, not recorded |

The four root commits, in two byte-identical pairs, are part of the same
problem.

**No commit on `main` has a fabricated-free ancestry.** Every one of the 329
descends from a commit with a fabricated author or an impossible date. There is
therefore no honest portion of the history to preserve — the corruption is at the
root, and anything built on it inherits it.

## The constraint that decides everything

Git requires an author and a date on every commit. There is no "author unknown"
and no "date unknown". So for a commit that cannot be honestly attributed, there
are exactly three options:

1. **Write a fabricated name and date.** That is what happened, and it is what
   we are trying to remove.
2. **Write a name and date that are true, but do not describe the original
   work** — for example, dating the commit to when the rewrite ran. This claims
   nothing false, but it stops being a record of the work.
3. **Delete the commit.**

Options 2 and 3 both discard the per-commit record. That is the price, and it is
unavoidable. There is no option that keeps a granular, verifiable, per-commit
history, because the granularity was never recorded honestly in the first place.

## Approach A — `--squash-import` (recommended)

Replaces the history with one commit holding the current source tree.

```bash
scripts/rewrite_history.sh --squash-import          # dry run
scripts/rewrite_history.sh --squash-import --apply
```

The replacement commit:

- **Author and committer** — the real owner, a real GitHub account.
- **Date** — the moment the commit was created. True by construction.
- **Message** — says what happened, how many commits were removed, and why.
- **Tree** — byte-identical to the tree that was there before. Verified before
  the replacement is written; the script aborts if the hash differs.

Every field in the result is true. Nothing is inferred, reconstructed, or
guessed. This is the only approach that satisfies the rule at the top of this
document.

What you lose: per-commit history, `git blame` across time, `git bisect`,
`git log`, and the ability to see how the code evolved.

What you keep: the entire codebase, byte for byte, plus an honest record of where
the metadata went and what it claimed.

### What `--squash-import` is not

It is not a "history rewrite" in the sense of preserving commits. It is a
deliberate deletion of unusable metadata, with the content carried forward
exactly. The script says so in the commit message it generates.

### The message is a judgement call, and it is editable

The generated message states the real numbers (commits removed, how many carried
impossible metadata) and points at the evidence document. If you want a shorter
message, edit the heredoc in the script before running it. What the message must
not do is claim the commit represents anything other than what it is.

## Approach B — `--mailmap` (not recommended)

Rewrites the author identity on every commit in place and keeps all of them.

```bash
scripts/rewrite_history.sh --mailmap                        # dry run
scripts/rewrite_history.sh --mailmap --apply --collapse-duplicate-roots
```

This preserves the commit graph. It has two problems that make it the weaker
choice:

1. **It attributes 181 commits to the repository owner on inference.** The
   inference is reasonable — the code came from the owner's GitLab and the other
   names do not exist — but it is still writing an attribution that cannot be
   checked, per commit, against anything. That is the same class of problem as
   the fabrication being removed, just in a more defensible direction.
2. **It leaves every fabricated timestamp in place.** Untouched, the history
   still contains commits dated before the repository existed.

The identity mapping is in [`scripts/provenance-mailmap.txt`](provenance-mailmap.txt).
Read it before running. If you prefer that those commits be explicitly
unattributed rather than attributed to the owner, change the target address on
each line to a marker such as `Unattributed <unattributed@invalid>` — that is
honest, and it needs no guesswork.

## Approach C — clamping the dates (removed)

An earlier version of this script moved impossible dates forward to a marker
constant. It has been deleted.

It is worth explaining why, because it looks reasonable. Clamping a commit dated
2025-01-14 to the repository-creation marker produces a date that is not false:
the commit really was created after the repository existed. But it is not the
date of the work either, and there is no way for a later reader to tell the
difference. It replaces an impossible date with a plausible-looking wrong one,
which is a strictly worse failure mode: an impossible date announces itself,
and a plausible one does not.

If the dates are unknowable, the honest options are "no commit history" or
"dates that say they are not the original dates". Not a marker dressed up as a
timestamp.

## Blast radius

Force-pushing a rewritten `main` breaks everyone who has ever cloned this
repository.

- **Every commit hash changes.** All of them.
- **Every open pull request** must be rebased or recreated. GitHub cannot merge
  a PR whose base was rewritten.
- **All clones must be re-cloned.** A plain `git pull` will merge the old
  history with the new one and reintroduce everything that was removed — this is
  the most common way a history cleanup silently fails.
- **36 remote branches diverge.** The stale `arena/*` session branches and the
  `dependabot/*` branches carry the old history.
- **Remote tags and GitHub Releases** point at commits that will not exist. See
  "Tags" below.
- **The contributor graph** rebuilds over time and may cache the old names.
- **Anything citing a commit SHA** — issues, logs, the evidence document —
  points at an object that may be gone.

## Runbook

```bash
# 1. Fresh clone, so nothing you care about is in your working tree
git clone https://github.com/Inkithai/Oyster360.git history-rewrite
cd history-rewrite

# 2. Dry run
scripts/rewrite_history.sh --squash-import

# 3. Apply to the local clone
scripts/rewrite_history.sh --squash-import --apply

# 4. Look at the result before publishing anything
git log --stat -1
git rev-parse main^{tree}      # must equal the tree the dry run printed
```

### What the run was verified to do

Executed end to end against a copy of this repository before being committed here:

```text
before:  329 commits on main, 4 roots on main, 213 commits with impossible metadata

after:   1 commit on main, 1 root, 0 fabricated identities

main tree before:  d38494ca8e20f36a4bd765b43808d0a9ad8824c7
main tree after:   d38494ca8e20f36a4bd765b43808d0a9ad8824c7   <- identical

fabricated identities on main:  0
commits on main:                1
```

The unchanged tree hash is the proof that no file content was altered.

### The backup

Written to `$TMPDIR/oyster360-history-backup-<stamp>/` before a single object is
changed:

| File | Why |
|---|---|
| `all-refs.bundle` | Full backup. `git clone` it to restore the old repository exactly. |
| `refs.txt` | Every ref and the object it pointed at. |
| `full-history-raw.txt` | `git log --format=raw` — the author, committer and date lines as they were. **After the rewrite this is the only copy of the metadata.** Keep it, or `ATTRIBUTION.md` becomes an unverifiable assertion. |

## Tags and releases

`v1.0.0` and `v1.1.0` point at commits that will no longer exist after the
rewrite. Re-tagging them onto the import commit would assert that a release
happened on that commit and that date, which is false. **Delete them and start
release history at the next genuine release:**

```bash
git push origin --delete v1.0.0 v1.1.0
```

While you are there: a first release for the rewritten repository is only honest
if the tag is created at the time and on the commit it actually represents.

## After publishing

1. Delete the stale `arena/*` and `dependabot/*` branches. They carry the old
   history and will reintroduce it if merged.
2. Update the README provenance section. It describes a history that will no
   longer exist. Replace it with the truth: **the history was removed on
   <date> because it was fabricated, the content was preserved byte-for-byte,
   and the evidence is in `docs/history_provenance_evidence.md`.**
3. Tell contributors to re-clone. Anyone who pulls instead of re-cloning will
   merge the old history back in.
4. Archive the backup somewhere durable. If it is lost, the claim that the
   history was fabricated cannot be checked.

## Rollback

Before the force-push, rollback is total and exact:

```bash
git clone <BACKUP_DIR>/all-refs.bundle restored
```

The restored repository has the original hashes, the original authors, and the
original dates — including the fabricated ones.

After the force-push, rollback means force-pushing the restore and invalidating
every clone that already pulled the new history. Decide before publishing, not
after.

## Why this document argues with itself

It explains at length why Approach A is correct, then documents how to run
Approach B, which it calls the weaker choice. That is deliberate. The choice
between "no history" and "history with attributed-on-inference authors" is a
values question about this project, not a technical one, and the repository
owner is the person who gets to answer it. The job of this document is to make
sure the answer is made knowingly, with the cost of each option stated.
