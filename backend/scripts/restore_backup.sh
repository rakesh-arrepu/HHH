#!/usr/bin/env bash
# placeholder backup restore script
if [[ "$1" == "--dry-run" ]]; then
  echo "Dry run: would restore backup"
else
  echo "Restoring backup..."
fi
