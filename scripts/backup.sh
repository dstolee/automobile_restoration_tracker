#!/usr/bin/env sh
set -eu
BACKUP_DIR=${1:-./backups}
STAMP=$(date +%Y-%m-%d_%H%M%S)
mkdir -p "$BACKUP_DIR"
tar -czf "$BACKUP_DIR/restoration-tracker-$STAMP.tar.gz" data
printf 'Backup written to %s\n' "$BACKUP_DIR/restoration-tracker-$STAMP.tar.gz"
