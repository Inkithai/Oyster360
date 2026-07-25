#!/bin/bash

# Oyster360 Database Backup Script
set -e

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="oyster360_backup_${TIMESTAMP}.sql"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

echo "Creating database backup..."

# Create backup
docker exec oyster360-postgres pg_dump -U ${DB_USER:-oyster360} ${DB_NAME:-oyster360} > ${BACKUP_DIR}/${BACKUP_FILE}

# Compress backup
gzip ${BACKUP_DIR}/${BACKUP_FILE}

echo "Backup created: ${BACKUP_DIR}/${BACKUP_FILE}.gz"

# Keep only last 7 days of backups
find $BACKUP_DIR -name "oyster360_backup_*.sql.gz" -mtime +7 -delete

echo "Backup completed successfully"