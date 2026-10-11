#!/usr/bin/env bash
#
# Remove fabricated metadata from this repository's history.
#
#   scripts/rewrite_history.sh --squash-import          # dry run (recommended path)
#   scripts/rewrite_history.sh --squash-import --apply
#
#   scripts/rewrite_history.sh --mailmap                # alternative, see below
#   scripts/rewrite_history.sh --mailmap --apply --collapse-duplicate-roots
#
# Two approaches, and they are not equivalent:
#
#   --squash-import  Replaces the history with a single commit containing the
#                    current source tree. Every field in the result is true:
#                    the author is the real owner, the timestamp is when the
#                    commit was created, and the message says what happened.
#                    Cost: no per-commit history, no blame across time, no
#                    bisect. This is the only approach that writes nothing
#                    fabricated.
#
#   --mailmap        Rewrites author identities in place and keeps all commits.
#                    It preserves granular history, but it attributes 181
#                    commits to the owner without evidence for any individual
#                    commit, and it keeps every fabricated timestamp. Use it
#                    only if keeping the commit graph matters more to you than
#                    keeping the metadata true.
#
# A third approach used to live here: clamping impossible dates forward to a
# marker. It was removed on purpose. See docs/history_rewrite.md.
#
# Guarantees, either way:
#   * NEVER pushes. NEVER creates or deletes a remote ref. NEVER touches the
#     network. The commands that publish the result are printed for a human.
#   * Writes a full backup bundle and a raw text record of the old history
#     before changing anything.
#   * Dry run by default. --apply is required to change a single object.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

MODE=""
APPLY=0
COLLAPSE_ROOTS=0
BRANCH="main"
AUTHOR="Inkithai Meiyalagan <108919130+Inkithai@users.noreply.github.com>"
BACKUP_DIR=""
MAILMAP="$ROOT/scripts/provenance-mailmap.txt"

usage() { sed -n '2,40p' "$0" | sed 's/^# \{0,1\}//'; exit "${1:-0}"; }

while [ $# -gt 0 ]; do
  case "$1" in
    --squash-import)   MODE="squash" ;;
    --mailmap)         MODE="mailmap" ;;
    --apply)           APPLY=1 ;;
    --collapse-duplicate-roots) COLLAPSE_ROOTS=1 ;;
    --branch)          BRANCH="$2"; shift ;;
    --branch=*)        BRANCH="${1#*=}" ;;
    --author)          AUTHOR="$2"; shift ;;
    --author=*)        AUTHOR="${1#*=}" ;;
    --backup-dir)      BACKUP_DIR="$2"; shift ;;
    --backup-dir=*)    BACKUP_DIR="${1#*=}" ;;
    -h|--help)         usage 0 ;;
    *) echo "unknown argument: $1" >&2; usage 1 ;;
  esac
  shift
done

fail() { printf '\n\033[1;31mrewrite_history: %s\033[0m\n' "$1" >&2; exit 1; }
say()  { printf '\n\033[1;36m== %s\033[0m\n' "$1"; }

[ -n "$MODE" ] || { echo "choose an approach: --squash-import or --mailmap" >&2; usage 1; }
[ -n "$BACKUP_DIR" ] || BACKUP_DIR="${TMPDIR:-/tmp}/oyster360-history-backup-$(date +%Y%m%d-%H%M%S)"

FAKE_RE='priya|marcus lee|sofia|daniel cho|elena vasquez|james wright|aisha rahman|thomas okonkwo|maya chen|your name'
REPO_CREATED_EPOCH=1783426278   # 2026-07-07T12:11:18Z, when the repository was created

# Commits whose author is fabricated or whose date predates the repository.
# Scope is passed in, because the branch being replaced and "everything in this
# clone" are different numbers and the commit message must state the right one.
count_fabricated_metadata() {
  git log "$1" --format='%an|%aI|%cI' | python3 -c '
import sys, datetime
fake = ("priya nair","marcus lee","sofia ramirez","daniel cho","elena vasquez",
        "james wright","aisha rahman","thomas okonkwo","maya chen","your name")
created = datetime.datetime(2026, 7, 7, 12, 11, 18, tzinfo=datetime.timezone.utc)
n = 0
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    author, authored, committed = line.split("|")
    if (author.lower() in fake
            or datetime.datetime.fromisoformat(authored) < created
            or datetime.datetime.fromisoformat(committed) < created):
        n += 1
print(n)'
}

say "Preflight"
git rev-parse --git-dir >/dev/null 2>&1 || fail "not inside a Git repository"
git rev-parse --verify "$BRANCH" >/dev/null 2>&1 || fail "branch not found: $BRANCH"
if git rev-parse --is-shallow-repository | grep -q true; then
  fail "shallow clone; rewriting it would produce a truncated history.
  Clone the full repository first: git clone https://github.com/Inkithai/Oyster360.git"
fi
if [ -n "$(git status --porcelain)" ]; then
  fail "working tree is not clean; commit or stash first"
fi

TOTAL=$(git rev-list "$BRANCH" --count)
TOTAL_ALL=$(git rev-list --all --count)
DIRTY=$(count_fabricated_metadata "$BRANCH")
TREE=$(git rev-parse "$BRANCH^{tree}")

say "What would change"
printf 'approach:                     %s\n' "$MODE"
printf 'branch:                       %s\n' "$BRANCH"
printf 'commits on %s:            %s\n' "$BRANCH" "$TOTAL"
printf '  of which metadata cannot be true: %s\n' "$DIRTY"
printf 'commits across all refs:      %s\n' "$TOTAL_ALL"
printf 'tree that must survive:       %s\n' "$TREE"
printf 'backup directory:             %s\n' "$BACKUP_DIR"

if [ "$MODE" = "squash" ]; then
  cat <<EOF

--squash-import replaces every commit with one commit holding the tree above.
The replacement commit will be authored as:

    $AUTHOR
    dated the moment it is created

Both of those are facts. Nothing in the replacement is invented, which is the
entire point: Git has no way to record "author unknown", so the alternatives
are to write a fabricated author and date, or to write one that is true.
EOF
else
  [ -f "$MAILMAP" ] || fail "mailmap not found: $MAILMAP"
  cat <<EOF

--mailmap keeps all $TOTAL commits and rewrites author identities using:

    $MAILMAP

Read that file before running. It attributes $DIRTY commits to the repository
owner without per-commit evidence, and it leaves every fabricated timestamp in
place. It preserves history at the cost of writing claims that cannot be
checked. --squash-import does not have that problem.
EOF
fi

if [ "$APPLY" -eq 0 ]; then
  say "DRY RUN — no objects were changed"
  cat <<EOF
Re-run with --apply to rewrite this clone. Nothing is pushed either way.

Backup written before any change:
  $BACKUP_DIR/all-refs.bundle        full backup of every ref
  $BACKUP_DIR/refs.txt               every ref and the object it pointed at
  $BACKUP_DIR/full-history-raw.txt   git log --format=raw: the author, committer
                                     and date lines as they are now

The raw dump is the evidence record once the objects are gone. Keep it.
EOF
  exit 0
fi

say "Backing up (1/3): full bundle of every ref"
mkdir -p "$BACKUP_DIR"
git bundle create "$BACKUP_DIR/all-refs.bundle" --all >/dev/null
echo "bundle: $BACKUP_DIR/all-refs.bundle"

say "Backing up (2/3): ref list"
git for-each-ref --format='%(objectname) %(objecttype) %(refname)' > "$BACKUP_DIR/refs.txt"
echo "refs recorded: $(wc -l < "$BACKUP_DIR/refs.txt" | tr -d ' ')"

say "Backing up (3/3): raw text record of the old history"
git log --all --format=raw > "$BACKUP_DIR/full-history-raw.txt"
echo "raw history lines: $(wc -l < "$BACKUP_DIR/full-history-raw.txt" | tr -d ' ')"

if [ "$MODE" = "mailmap" ]; then
  command -v git-filter-repo >/dev/null 2>&1 || fail "git-filter-repo not found.
  Install it, then re-run:
    pipx install git-filter-repo
    # or: python3 -m pip install --user git-filter-repo"
  say "Rewriting authorship in place"
  git-filter-repo --mailmap "$MAILMAP" --force
  if [ "$COLLAPSE_ROOTS" -eq 1 ]; then
    say "Collapsing duplicate roots (same tree, different author/date)"
    python3 - <<'PY' > "$BACKUP_DIR/root-collapse.txt"
import collections, subprocess

def sh(*a):
    return subprocess.run(a, capture_output=True, text=True).stdout.strip()

groups = collections.defaultdict(list)
for root in sh("git", "rev-list", "--max-parents=0", "--all").split("\n"):
    if root:
        groups[sh("git", "log", "-1", "--format=%T", root)].append(root)
for tree, roots in sorted(groups.items()):
    if len(roots) < 2:
        continue
    on_main = [r for r in roots
               if subprocess.run(["git", "merge-base", "--is-ancestor", r, "main"],
                                 capture_output=True).returncode == 0]
    keeper = sorted(on_main or roots,
                    key=lambda r: sh("git", "log", "-1", "--format=%ct", r))[-1]
    for r in roots:
        if r != keeper:
            print("%s\t%s\t%s" % (r, keeper, tree[:8]))
PY
    if [ -s "$BACKUP_DIR/root-collapse.txt" ]; then
      while IFS=$'\t' read -r DROP KEEP ROOTTREE; do
        echo "  ${DROP:0:8} -> ${KEEP:0:8}  (tree $ROOTTREE)"
        git replace "$DROP" "$KEEP"
      done < "$BACKUP_DIR/root-collapse.txt"
      git-filter-repo --force --replace-refs delete-no-add >/dev/null
    else
      echo "no duplicate roots found"
    fi
  fi
else
  say "Replacing history with a single import commit"
  MSG="$(mktemp)"
  cat > "$MSG" <<EOF
Oyster360: source tree imported; fabricated history removed

This commit holds the repository's complete source tree. It replaces the
previous history, which could not be repaired: $TOTAL commits, of which $DIRTY
carried metadata that cannot be true — author identities with no GitHub
accounts, dates earlier than the repository's own creation, and duplicated
root commits. No commit in that history had a fabricated-free ancestry, so
there was no honest portion of it to carry forward.

The old commits were not rewritten in place because Git requires an author and
a date on every commit. Rewriting them would have meant replacing one set of
invented names and dates with another set of invented names and dates. This
commit claims nothing that cannot be checked: its author is the repository's
owner and its date is when it was created.

Evidence for the removed history — identities, addresses, hashes, timestamps,
tag objects and release notes — is recorded in
docs/history_provenance_evidence.md.
EOF
  NEW=$(GIT_AUTHOR_NAME="${AUTHOR%% <*}" \
        GIT_AUTHOR_EMAIL="${AUTHOR##*<}" \
        GIT_COMMITTER_NAME="${AUTHOR%% <*}" \
        GIT_COMMITTER_EMAIL="${AUTHOR##*<}" \
        git commit-tree "$TREE" -F "$MSG")
  rm -f "$MSG"

  NEW_TREE=$(git rev-parse "$NEW^{tree}")
  if [ "$NEW_TREE" != "$TREE" ]; then
    fail "content check failed: replacement tree $NEW_TREE differs from $TREE"
  fi
  echo "replacement commit: $NEW"
  echo "content check:      identical tree ($NEW_TREE)"

  git update-ref "refs/heads/$BRANCH" "$NEW"
  git symbolic-ref HEAD "refs/heads/$BRANCH" 2>/dev/null || true
  git reset -q --hard "$BRANCH"
fi

say "Verification"
BRANCH_DIRTY=$(git log "$BRANCH" --format='%an <%ae>' | grep -ciE "$FAKE_RE" || true)
OTHER_DIRTY=$(git log --all --format='%an <%ae>' | grep -ciE "$FAKE_RE" || true)
printf 'fabricated identities on %s:   %s\n' "$BRANCH" "$BRANCH_DIRTY"
printf 'commits on %s:                 %s\n' "$BRANCH" "$(git rev-list "$BRANCH" --count)"
printf 'roots on %s:                   %s\n' "$BRANCH" "$(git rev-list --max-parents=0 "$BRANCH" | wc -l | tr -d ' ')"
printf '%s tree now:                  %s\n' "$BRANCH" "$(git rev-parse "$BRANCH^{tree}")"
[ "$BRANCH_DIRTY" = "0" ] || fail "fabricated identities survived on $BRANCH; restore from the backup and investigate"
if [ "$OTHER_DIRTY" != "0" ]; then
  echo
  echo "Note: $(git rev-list --all --count) commits still carry fabricated metadata across"
  echo "      the other refs ($OTHER_DIRTY of them by a fabricated author). Only $BRANCH was"
  echo "      rewritten. Those refs are stale branches and remote tags — delete them as"
  echo "      described below, or they will reintroduce the old history if merged."
fi

cat <<EOF

$(say "Next steps — run these yourself, deliberately")

Nothing was pushed. Tags and other branches still point at the old history and
will need handling by hand:

  git log --oneline -3                     # look at the result first
  git bundle verify "$BACKUP_DIR/all-refs.bundle"

  # Remote tags v1.0.0 and v1.1.0 point at commits that no longer exist here.
  # Re-tagging them onto the import commit would assert a release that did not
  # happen, so delete them instead and start release history from the next
  # genuine release:
  git push --force-with-lease origin $BRANCH
  git push origin --delete v1.0.0 v1.1.0

Then:

  1. Delete the stale arena/* and dependabot/* branches; they carry the old
     history and will reintroduce it if merged.
  2. Update the README provenance section. It currently describes a history
     that will no longer exist. Replace it with the truth: the history was
     removed on <date> because it was fabricated, the content was preserved
     byte-for-byte, and the evidence is in docs/history_provenance_evidence.md.
  3. Keep or archive the backup. If you delete it and the raw dump, the
     evidence record becomes unverifiable.
  4. Tell contributors to re-clone. Every existing clone still holds the old
     history and will merge it back on a pull.

Backup kept at: $BACKUP_DIR
EOF
