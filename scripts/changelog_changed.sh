#!/usr/bin/env bash
set -eo pipefail

# This script is meant to be invoked by pre-commit in serial mode, so that it
# has the entire list of files in the arguments.

# This script takes in a list of files. It determines if any of those
# files are in a folder (or subfolder of a folder) that has a CHANGELOG.md file,
# and if so, it will make sure the CHANGELOG is also in its list of arguments.
# Essentially what this does is make sure that if you make a change to a file,
# and that change *should* be tracked in a Changelog, that that change *is*
# tracked in a changelog.

# It's not terribly smart: it doesn't ensure that the change to the Changelog
# actually reflects anything about the code changes themselves.

# shellcheck disable=SC2317 # we use unreachable commands to turn off verbose logging
function log() {
  return 0
  echo "$1"
}

log "files:"
log "$@"
log ""

code=0

existing_changelogs=$(find . -name "CHANGELOG.md" -not -path "*/.terraform/*" -not -path "./terraform/modules/*/modules/*")
log "existing changelogs:"
log "$existing_changelogs"
log ""

changed_changelogs=$(find "$@" -name "CHANGELOG.md" -not -path "*/.terraform/*")
log "changed changelogs:"
log "$changed_changelogs"
log ""

# For each file in the invocation...
for f in "$@"
do
  log "f=$f"
  # ...and each CHANGELOG.md under the current directory...
  for ch in $existing_changelogs
  do
    ch=${ch#*/} # remove prefix ending in /
    log "  ch=$ch"
    # ...search in the CHANGELOG.md's parent directory for the file.
    log "  find \"\$(dirname \"$ch\")\" -not -path "*/.terraform/*" -path \"$f\" | wc -l"
    found=$(find "$(dirname "$ch")" -not -path "*/.terraform/*" -path "$f" | wc -l)
    # If the file is under the CHANGELOG's parent directory, then that CHANGELOG should have been changed
    if [ "$found" -gt 0 ]; then
      log "  found one for $ch $f"
      if [[ ! "$changed_changelogs" =~ $ch ]]; then
        echo "$f changed but $ch did not!"
        code=1
      fi
    fi
  done
done

exit $code
