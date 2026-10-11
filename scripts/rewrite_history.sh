#!/usr/bin/env bash
#
# Rewrite this repository's LOCAL history to remove fabricated authorship.
#
#   scripts/rewrite_history.sh                  # dry run: report what would change
#   scripts/rewrite_history.sh --apply          # rewrite the clone you are standing in
#   scripts/rewrite_history.sh --apply --collapse-duplicate-roots
#   scripts/rewrite_history.sh --apply --normalize-dates
#
# --collapse-duplicate-roots merges root commits that share a tree hash but
# record different authors and dates. Identical tree means identical files, so
# the only thing dropped is the duplicate claim about who and when.
# --normalize-dates moves provably impossible dates onto a marker. Read
# docs/history_rewrite.md before using it: it does not recover the truth.
#
# Guarantees, because history rewriting has no undo button:
#
#   * NEVER pushes. NEVER deletes or creates a remote ref. NEVER contacts the
#     network. The commands that publish the result are printed for a human to
#     run deliberately — see "Next steps" in the output.
#   * Writes a full backup bundle and a raw text record of the old history
#     before touching anything.
#   * Dry run by default. --apply is required to change a single object.
#
# Read docs/history_rewrite.md first. It explains what this rewrite fixes, what
# it cannot fix, and why rewriting the timestamps is a decision you should make
# on purpose rather than by running a script.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

APPLY=0
NORMALIZE_DATES=""
COLLAPSE_ROOTS=0
BACKUP_DIR=""
MAILMAP="$ROOT/scripts/provenance-mailmap.txt"
DATE_CALLBACK="$ROOT/scripts/rewrite_dates_callback.py"
REPO_CREATED_ISO="2026-07-07T12:11:18Z"

usage() { sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'; exit "${1:-0}"; }

while [ $# -gt 0 ]; do
  case "$1" in
    --apply)           APPLY=1 ;;
    --normalize-dates) NORMALIZE_DATES="$REPO_CREATED_ISO" ;;
    --normalize-dates=*) NORMALIZE_DATES="${1#*=}" ;;
    --collapse-duplicate-roots) COLLAPSE_ROOTS=1 ;;
    --mailmap)         MAILMAP="$2"; shift ;;
    --mailmap=*)       MAILMAP="${1#*=}" ;;
    --backup-dir)      BACKUP_DIR="$2"; shift ;;
    --backup-dir=*)    BACKUP_DIR="${1#*=}" ;;
    -h|--help)         usage 0 ;;
    *) echo "unknown argument: $1" >&2; usage 1 ;;
  esac
  shift
done

fail() { printf '\n\033[1;31mrewrite_history: %s\033[0m\n' "$1" >&2; exit 1; }
say()  { printf '\n\033[1;36m== %s\033[0m\n' "$1"; }

# Roots sharing a tree hash are the same commit recorded more than once under
# different authors and dates. Collapsing them keeps the tree and drops the
# duplicate: nothing in the working files changes, only the claim about who
# committed them and when. Output: "drop-sha<TAB>keep-sha<TAB>tree".
plan_root_collapse() {
  python3 - <<'PY'
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
    pool = on_main or roots
    keeper = sorted(pool, key=lambda r: sh("git", "log", "-1", "--format=%ct", r))[-1]
    for r in roots:
        if r != keeper:
            print("%s\t%s\t%s" % (r, keeper, tree[:8]))
PY
}

[ -n "$BACKUP_DIR" ] || BACKUP_DIR="${TMPDIR:-/tmp}/oyster360-history-backup-$(date +%Y%m%d-%H%M%S)"

say "Preflight"
git rev-parse --git-dir >/dev/null 2>&1 || fail "not inside a Git repository"
[ -f "$MAILMAP" ] || fail "mailmap not found: $MAILMAP"
[ -f "$DATE_CALLBACK" ] || fail "date callback not found: $DATE_CALLBACK"
if command -v git-filter-repo >/dev/null 2>&1; then
  FR="git-filter-repo"
  echo "git-filter-repo: $(command -v git-filter-repo)"
else
  fail "git-filter-repo not found.
  Install it, then re-run:
    pipx install git-filter-repo
    # or: python3 -m pip install --user git-filter-repo
    # or: https://github.com/newren/git-filter-repo"
fi

if git rev-parse --is-shallow-repository | grep -q true; then
  fail "this is a shallow clone; rewriting it would produce a truncated history.
  Clone the full repository first:  git clone https://github.com/Inkithai/Oyster360.git"
fi

if [ -n "$(git status --porcelain)" ]; then
  fail "working tree is not clean; commit or stash first (a rewrite moves every commit)"
fi

IDENT_TOTAL=$(git log --all --format='%an <%ae>' | sort -u | wc -l | tr -d ' ')
FAKE_PATTERNS=$(grep -v '^#' "$MAILMAP" | grep -v '^$' | awk '{$1="";$2="";sub(/^ +/,"");print}' | sort -u | wc -l | tr -d ' ')

say "What this rewrite would change"
printf 'mailmap:            %s\n' "$MAILMAP"
printf 'distinct authors:   %s across all refs\n' "$IDENT_TOTAL"
printf 'identities mapped:  %s\n' "$FAKE_PATTERNS"
printf 'root commits:       %s\n' "$(git rev-list --max-parents=0 --all | wc -l | tr -d ' ')"
printf 'refs that will be rewritten: %s\n' "$(git for-each-ref --format='%(refname)' | wc -l | tr -d ' ')"
printf 'backup directory:   %s\n' "$BACKUP_DIR"

if [ "$COLLAPSE_ROOTS" -eq 1 ]; then
  echo
  echo "Duplicate roots that would be collapsed (same tree, different author/date):"
  plan_root_collapse | awk -F'\t' '{printf "  %s -> %s  (tree %s)\n", substr($1,1,8), substr($2,1,8), $3}'
fi

if [ "$APPLY" -eq 0 ]; then
  say "DRY RUN — no objects were changed"
  cat <<EOF
Re-run with --apply to rewrite this clone.

What --apply runs, in order:

  1. git bundle create "$BACKUP_DIR/all-refs.bundle" --all
  2. git for-each-ref                     > "$BACKUP_DIR/refs.txt"
  3. git log --all --format=raw           > "$BACKUP_DIR/full-history-raw.txt"
  4. $FR --mailmap "$MAILMAP" --force
$( [ "$COLLAPSE_ROOTS" -eq 1 ] && echo "  5. git replace <duplicate-root> <kept-root> ... && $FR --force --replace-refs delete-no-add" )
$( [ -n "$NORMALIZE_DATES" ] && echo "  6. $FR --force --commit-callback \"\$(cat $DATE_CALLBACK)\"" )

Step 3 matters more than it looks: the raw dump is the only record of the old
author/committer/dates once the objects are rewritten. Keep it.

Nothing is pushed. Nothing outside this clone is touched.
EOF
  exit 0
fi

say "Backing up (1/3): full bundle of every ref"
mkdir -p "$BACKUP_DIR"
git bundle create "$BACKUP_DIR/all-refs.bundle" --all
echo "bundle: $BACKUP_DIR/all-refs.bundle"

say "Backing up (2/3): ref list"
git for-each-ref --format='%(objectname) %(objecttype) %(refname)' > "$BACKUP_DIR/refs.txt"
wc -l < "$BACKUP_DIR/refs.txt" | tr -d ' ' | xargs echo "refs recorded:"

say "Backing up (3/3): raw text record of the old history"
# The evidence that the README describes lives in these lines. After a rewrite
# the objects no longer carry them, so keep this file.
git log --all --format=raw > "$BACKUP_DIR/full-history-raw.txt"
wc -l < "$BACKUP_DIR/full-history-raw.txt" | tr -d ' ' | xargs echo "raw history lines:"

say "Rewriting authorship"
$FR --mailmap "$MAILMAP" --force

if [ "$COLLAPSE_ROOTS" -eq 1 ]; then
  say "Collapsing duplicate roots"
  # Compute the plan against the rewritten history: root hashes have changed.
  PLAN="$(plan_root_collapse)"
  if [ -z "$PLAN" ]; then
    echo "no duplicate roots found; nothing to collapse"
  else
    printf '%s\n' "$PLAN" | while IFS=$'\t' read -r DROP KEEP TREE; do
      echo "  ${DROP:0:8} -> ${KEEP:0:8}  (tree $TREE)"
      git replace "$DROP" "$KEEP"
    done
    $FR --force --replace-refs delete-no-add
  fi
fi

if [ -n "$NORMALIZE_DATES" ]; then
  say "Normalizing impossible dates to the marker $NORMALIZE_DATES"
  echo "NOTE: the marker is not when the work happened. The real dates are not"
  echo "      knowable. See docs/history_rewrite.md before deciding this is better."
  $FR --force --commit-callback "$(cat "$DATE_CALLBACK")"
fi

say "Verification"
REMAINING=$(git log --all --format='%an <%ae>' | sort -u | grep -ciE 'priya|marcus lee|sofia|daniel cho|elena vasquez|james wright|aisha rahman|thomas okonkwo|maya chen|your name' || true)
printf 'fabricated identities still present: %s\n' "$REMAINING"
printf 'commits across all refs:            %s\n' "$(git rev-list --all --count)"
printf 'root commits remaining:             %s\n' "$(git rev-list --max-parents=0 --all | wc -l | tr -d ' ')"
[ "$REMAINING" = "0" ] || fail "some fabricated identities survived; inspect the mailmap before publishing"

cat <<EOF

$(say "Next steps — run these yourself, deliberately")

This clone is now rewritten. git-filter-repo removed the 'origin' remote so this
cannot be pushed by accident. To publish:

  git remote add origin https://github.com/Inkithai/Oyster360.git
  git log --oneline -5                      # look at it before you push
  git bundle verify "$BACKUP_DIR/all-refs.bundle"

  # Tags: every v0.x tag is deleted as part of this cleanup; v1.0.0 and v1.1.0
  # must be recreated on the rewritten commits, because their old objects no
  # longer exist. Do not force-push them silently.
  git push --force-with-lease origin main
  git push origin --delete v0.1.0 v0.2.0 v0.3.0 v0.4.0 v0.5.0 v0.6.0 v0.7.0 v0.8.0 v0.9.0

Then, in order:

  1. Recreate any tag you are keeping against the rewritten commit, and update
     the GitHub Release for it.
  2. Delete the stale branches listed in docs/history_rewrite.md — their commits
     are no longer ancestors of the rewritten main.
  3. Update the README provenance section: after a rewrite the old hashes in
     docs/history_provenance_evidence.md no longer resolve from this repository.
     Keep the raw history dump somewhere it can be produced on request, or the
     disclosure becomes unverifiable.
  4. Tell contributors to re-clone. Force-pushing main invalidates every clone
     and every open pull request.

Backup kept at: $BACKUP_DIR
EOF
