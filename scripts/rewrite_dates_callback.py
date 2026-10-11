# git-filter-repo commit callback — NOT a standalone script.
#
# Used by scripts/rewrite_history.sh as:
#     git filter-repo --force --commit-callback "$(cat scripts/rewrite_dates_callback.py)"
#
# git-filter-repo exec()s this file with a `commit` object bound in scope. It is
# never imported and never run directly, which is why it has no __main__.
#
# What it does: any author or committer timestamp that predates the creation of
# the GitHub repository (2026-07-07T12:11:18Z) is moved forward to that instant.
# Those dates are provably impossible, so clamping removes an assertion that
# cannot be true.
#
# What it does NOT do: recover when the work actually happened. Nobody knows.
# The code arrived in this repository as a copy from a private GitLab, and the
# dates attached to it were constructed afterwards. Clamping replaces a
# fabricated date with a different, equally uninformative one — the difference
# is that the marker does not pretend to be a record.
#
# If that trade is not what you want, do not pass --normalize-dates. Leaving the
# dates alone and documenting them, which is what the README currently does, is
# the other defensible answer. There is no option that produces true dates,
# because the true dates were never captured.

_MARKER_EPOCH = 1783426278  # 2026-07-07T12:11:18Z, repository creation


def _clamp(value):
    """Move a 'seconds +0000' timestamp forward to the marker if it predates it."""
    as_bytes = isinstance(value, bytes)
    text = value.decode() if as_bytes else value
    parts = text.split()
    if len(parts) != 2:
        return value
    try:
        ts = int(parts[0])
    except ValueError:
        return value
    if ts >= _MARKER_EPOCH:
        return value
    if as_bytes:
        return b"%d %s" % (_MARKER_EPOCH, parts[1].encode())
    return "%d %s" % (_MARKER_EPOCH, parts[1])


commit.author_date = _clamp(commit.author_date)
commit.committer_date = _clamp(commit.committer_date)
