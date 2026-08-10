#!/bin/bash

set -euo pipefail

BACKUP_ROOT="/backup/symptomtracker"
SOURCE_DIR="/opt/symptomtracker"

TIMESTAMP="$(date '+%Y-%m-%d_%H-%M-%S')"
BACKUP_DIR="${BACKUP_ROOT}/${TIMESTAMP}"

DB_CONTAINER="family-db"
DB_NAME="symptomtracker"
DB_USER="familyuser"

LOG_FILE="${BACKUP_ROOT}/backup.log"


log()
{
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" \
        >> "${LOG_FILE}"
}


cleanup_failed_backup()
{
    if [ -d "${BACKUP_DIR}" ]; then
        rm -rf "${BACKUP_DIR}"
    fi
}


trap 'log "HIBA: a mentés megszakadt."; cleanup_failed_backup' ERR


mkdir -p "${BACKUP_DIR}"

log "SymptomTracker backup indul: ${TIMESTAMP}"


# PostgreSQL adatbázis

docker exec \
    "${DB_CONTAINER}" \
    pg_dump \
    -U "${DB_USER}" \
    -d "${DB_NAME}" \
    -Fc \
    > "${BACKUP_DIR}/symptomtracker.dump"


# Teljes alkalmazás, beleértve:
# - forráskód
# - .env
# - uploads
# - migrations
# - Git repository
# - venv

tar \
    --exclude='symptomtracker/.gunicorn' \
    --exclude='symptomtracker/.cache' \
    --exclude='symptomtracker/__pycache__' \
    --exclude='symptomtracker/app/__pycache__' \
    -czf "${BACKUP_DIR}/symptomtracker-files.tar.gz" \
    -C /opt \
    symptomtracker

# Ellenőrizzük, hogy ténylegesen létrejöttek-e.

test -s "${BACKUP_DIR}/symptomtracker.dump"
test -s "${BACKUP_DIR}/symptomtracker-files.tar.gz"


# 3 napnál régebbi időbélyeges backup könyvtárak törlése.
# A backup.log természetesen megmarad.

find "${BACKUP_ROOT}" \
    -mindepth 1 \
    -maxdepth 1 \
    -type d \
    -mmin +4320 \
    -exec rm -rf {} \;


log "SymptomTracker backup sikeres: ${BACKUP_DIR}"

trap - ERR

exit 0
