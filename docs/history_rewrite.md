# Rewriting the repository history

This is the plan for removing fabricated authorship, duplicate roots and
impossible dates from the Git history itself. It is written to be reviewed and
executed deliberately, by hand, by the repository owner. **Nothing in this
repository runs it automatically, and CI never touches history.**

The evidence the rewrite is based on is in
[history_provenance_evidence.md](history_provenance_evidence.md); the reasoning
behind leaving the history documented rather than rewriting it is in the
[README](../README.md#repository-history-and-provenance).

## Start here: decide whether to rewrite at all

Every rewrite trades one problem for another. Read this before running anything.

**What a rewrite can fix**

| Problem | After the rewrite |
|---|---|
| 181 of 329 commits on `main` attributed to ten people who never existed | Every commit attributed to a real identity, or to a clearly-labelled marker |
| Four unrelated root commits, in two byte-identical pairs | Duplicate roots collapsed; content unchanged, because the trees are identical |
| Commits dated before the repository existed | Impossible dates removed or moved to a documented marker |
| Tags whose tagger timestamp precedes the commit they point at | Tags recreated on rewritten commits with honest dates |

**What a rewrite cannot fix**

- **It cannot recover the true dates.** The code was copied into this
  repository from a private GitLab. The real authorship dates of those 181
  commits were never captured here, and nothing in the repository reconstructs
  them. Clamping a 2025-01-14 date to a 2026-07-07 marker does not make it true;
  it swaps a fabricated date for a different fabricated date that happens not to
  look wrong. `--normalize-dates` does exactly that, which is why it is opt-in
  and why it prints a warning.
- **It cannot make the history verifiable.** Right now the README's claims can be
  checked by anyone with a clone: the hashes, tree collisions and timestamps are
  all still there. After a rewrite they are not, and the old hashes in
  [history_provenance_evidence.md](history_provenance_evidence.md) stop resolving
  from this repository. The disclosure becomes an assertion about history that no
  longer exists in the repository — which is a weaker position than the current
  one, not a stronger one.
- **It cannot un-publish what was published.** Forks, clones and the contributor
  graph are outside the owner's control.

The honest summary: a rewrite makes the repository *tidier*, not *more truthful*.
If the goal is that no reader is misled, the current approach — keep the
fabricated history, document it precisely — already achieves that, and achieves
it verifiably. If the goal is that the repository no longer carries 181 false
attributions, a rewrite is the only way to get there, and the evidence record
becomes the substitute for the history it replaces.

## Blast radius

Force-pushing a rewritten `main` is a breaking change for everyone who has ever
cloned this repository:

- **Every commit hash changes.** All of them.
- **36 remote branches** diverge. The stale `arena/*` session branches and the
  `dependabot/*` branches stop sharing ancestry with `main`; most can be deleted.
- **Every open pull request** must be rebased or recreated. GitHub cannot merge a
  PR whose base has been rewritten.
- **All existing clones** must be re-cloned. A `git pull` will merge the old and
  new histories and reintroduce everything the rewrite removed.
- **The contributor graph** rebuilds over time and may cache the old attribution.
- **GitHub Releases** attached to rewritten tags need updating by hand.
- **Anything referencing a commit SHA** — issue comments, CI logs, the evidence
  document, blog posts — points at an object that may no longer exist.

## Prerequisites

- `git-filter-repo` (the script checks for it and explains how to install it).
- A full, non-shallow clone. The script refuses to run in a shallow clone,
  because rewriting one produces a truncated history.
- A clean working tree.
- Time to tell every contributor to re-clone.

## Runbook

Run all of this yourself. The script never pushes and never touches a remote.

```bash
# 1. Fresh clone, so nothing you care about is in the working tree
git clone https://github.com/Inkithai/Oyster360.git history-rewrite
cd history-rewrite

# 2. Read the identity mapping and change anything you disagree with
$EDITOR scripts/provenance-mailmap.txt

# 3. Dry run: reports what would change, touches nothing
scripts/rewrite_history.sh --collapse-duplicate-roots

# 4. Rewrite the local clone
scripts/rewrite_history.sh --apply --collapse-duplicate-roots

#    Add --normalize-dates only if you have decided that a marker date is
#    better than an impossible date. It is not more truthful. Your call.
```

The script writes three things to `$TMPDIR/oyster360-history-backup-<stamp>/`
before it changes a single object:

| File | Why it matters |
|---|---|
| `all-refs.bundle` | Full backup. `git clone` it to get the old repository back. |
| `refs.txt` | Every ref and the object it pointed at. |
| `full-history-raw.txt` | `git log --format=raw`: the author, committer and date lines as they were. **This is the evidence record once the objects are gone. Keep it.** |

### What the run was verified to do

The pipeline was tested end to end against a copy of this repository before
being committed here. Results, so you know what to expect:

```text
before:  329 commits on main, 4 roots on main, 233 commits by fabricated
         identities across all refs
after:   327 commits on main, 2 roots on main, 0 commits by fabricated identities

main tree hash before:  d38494ca8e20f36a4bd765b43808d0a9ad8824c7
main tree hash after:   d38494ca8e20f36a4bd765b43808d0a9ad8824c7   <- identical
```

The commit count drops by two because the two duplicate roots are merged; the
tree hash is unchanged, which is the proof that no file content was altered by
the rewrite. Check that hash yourself after step 4 — if it differs, stop and
restore from the bundle.

## Roots: what happens to them

The history contains three commits with the tree `3dfc1663` and three with the
tree `52d941c1`, under different authors and dates. Identical tree means
identical files, so the duplicates are the same commit recorded more than once.

`--collapse-duplicate-roots` groups roots by tree, keeps the member that is an
ancestor of `main` (falling back to the most recent), and replaces the others
with it via `git replace`, made permanent by a second `filter-repo` pass.

After that, **two roots remain**, because the repository genuinely descends from
two different starting points: a project skeleton ("chore: initialize project
repository") and a code import ("copied from my gitlab"). Collapsing those two
into one would mean inventing an order for them. The rewrite does not do that,
and neither should you without a reason you can state.

## Publishing, after you have checked the result

```bash
git remote add origin https://github.com/Inkithai/Oyster360.git
git bundle verify "$BACKUP_DIR/all-refs.bundle"   # backup is readable
git log --oneline -20                             # read before you push

git push --force-with-lease origin main
git push origin --delete v0.1.0 v0.2.0 v0.3.0 v0.4.0 v0.5.0 v0.6.0 v0.7.0 v0.8.0 v0.9.0
```

Then, in order:

1. Recreate `v1.0.0` and `v1.1.0` on their rewritten commits and update the
   `v1.0.0` GitHub Release. Their old tag objects no longer exist.
2. Delete the stale `arena/*` and `dependabot/*` branches. Their commits are no
   longer ancestors of the rewritten `main`.
3. Rewrite the README provenance section: after a rewrite, the four-root and
   five-identical-timestamp findings no longer apply, and the disclosure has to
   say so rather than continue to assert them. You are not removing the
   disclosure — you are updating it to describe the history that now exists,
   including that it was rewritten.
4. Say plainly, somewhere permanent, that the history was rewritten on a given
   date and why. A rewritten history with no note is worse than the fabricated
   one, because nothing in it looks wrong.
5. Tell contributors to re-clone, and delete the evidence backup or move it
   somewhere durable. If you delete it, the disclosure becomes unverifiable.

## Rollback

Before the force-push, rollback is total: `git clone <BACKUP_DIR>/all-refs.bundle`
reconstructs the original repository, hashes and all.

After the force-push, rollback means force-pushing the restore. Forks and
clones that already pulled the rewritten history will then diverge again.
Rewriting history twice is worse than rewriting it once, so decide before
publishing rather than after.
