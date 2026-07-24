# Backup and restore

## Backup

For a consistent simple backup, stop the application briefly and archive the data directory:

```bash
docker compose stop
tar -czf restoration-backup-$(date +%F).tar.gz data
docker compose start
```

## Restore

```bash
docker compose down
mv data data.old
mkdir data
tar -xzf restoration-backup-YYYY-MM-DD.tar.gz
docker compose up -d
```

Confirm ownership and permissions if the archive came from another machine. Retain `data.old` until the restored application has been verified.
