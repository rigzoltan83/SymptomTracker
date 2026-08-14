#!/usr/bin/env bash

set -euo pipefail


SCRIPT_DIR="$(
    cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
    pwd
)"

PROJECT_DIR="$(
    cd -- "${SCRIPT_DIR}/.."
    pwd
)"

LIB_DIR="${SCRIPT_DIR}/lib"

DRY_RUN=false

APP_PORT_START=5060
APP_PORT_END=5199

DB_PORT_START=5432
DB_PORT_END=5499

INSTALL_DIR="/opt/symptomtracker"


# =========================================================
# PARAMÉTEREK
# =========================================================

for arg in "$@"; do
    case "$arg" in
        --dry-run)
            DRY_RUN=true
            ;;

        *)
            echo "Unknown option: $arg" >&2
            exit 2
            ;;
    esac
done


# =========================================================
# KÖZÖS FÜGGVÉNYEK
# =========================================================

if [ ! -f "${LIB_DIR}/common.sh" ]; then
    echo "Missing file: ${LIB_DIR}/common.sh" >&2
    exit 1
fi

# shellcheck source=/dev/null
source "${LIB_DIR}/common.sh"


# =========================================================
# NYELVVÁLASZTÁS
# =========================================================

echo
echo "SymptomTracker"
echo
echo "1) Magyar"
echo "2) English"
echo

while true; do
    printf "Language / Nyelv [1/2]: "
    read -r language_choice

    case "$language_choice" in
        1|hu|HU)
            LANGUAGE="hu"
            break
            ;;

        2|en|EN)
            LANGUAGE="en"
            break
            ;;

        *)
            echo "1 / 2"
            ;;
    esac
done


MESSAGE_FILE="${LIB_DIR}/messages_${LANGUAGE}.sh"

if [ ! -f "$MESSAGE_FILE" ]; then
    echo "Missing language file: $MESSAGE_FILE" >&2
    exit 1
fi

# shellcheck source=/dev/null
source "$MESSAGE_FILE"


echo
echo "========================================"
echo "$MSG_TITLE"
echo "========================================"
echo

if [ "$DRY_RUN" = true ]; then
    echo "$MSG_DRY_RUN"
    echo
fi


# =========================================================
# FÁJLOK
# =========================================================

required_files=(
    "${PROJECT_DIR}/requirements.txt"
    "${PROJECT_DIR}/docker-compose.yml"
    "${PROJECT_DIR}/seed/reference_data.json"
    "${PROJECT_DIR}/scripts/import_reference_seed.py"
    "${PROJECT_DIR}/migrations/alembic.ini"
    "${PROJECT_DIR}/run.py"
)

for filename in "${required_files[@]}"; do
    if [ ! -f "$filename" ]; then
        echo "$MSG_FAILED"
        echo "Missing file: $filename" >&2
        exit 1
    fi
done

echo "$MSG_FILES_OK"


# =========================================================
# PYTHON
# =========================================================

if ! command -v python3 >/dev/null 2>&1; then
    echo "$MSG_FAILED"
    echo "python3" >&2
    exit 1
fi

PYTHON_VERSION="$(
    python3 --version 2>&1
)"

echo "$MSG_PYTHON_OK"
echo "  $PYTHON_VERSION"


# =========================================================
# DOCKER
# =========================================================

if ! command -v docker >/dev/null 2>&1; then
    echo "$MSG_FAILED"
    echo "Docker" >&2
    exit 1
fi

echo "$MSG_DOCKER_OK"
echo "  $(docker --version)"


if ! docker compose version >/dev/null 2>&1; then
    echo "$MSG_FAILED"
    echo "Docker Compose" >&2
    exit 1
fi

echo "$MSG_COMPOSE_OK"
echo "  $(docker compose version)"

echo
echo "$MSG_REQUIREMENTS_OK"

# =========================================================
# MEGLÉVŐ TELEPÍTÉS VÉDELME
# =========================================================

existing_install=false


if [ -f "${INSTALL_DIR}/.env" ]; then
    echo
    echo "$MSG_EXISTING_ENV"

    existing_install=true
fi


if docker ps -a \
    --format '{{.Names}}' \
    | grep -Fxq 'symptomtracker-db'
then
    echo
    echo "$MSG_EXISTING_CONTAINER"

    existing_install=true
fi


if systemctl list-unit-files \
    --type=service \
    --no-legend \
    2>/dev/null \
    | awk '{print $1}' \
    | grep -Fxq 'symptomtracker.service'
then
    echo
    echo "$MSG_EXISTING_SERVICE"

    existing_install=true
fi


if [ "$existing_install" = true ]; then
    echo
    echo "$MSG_EXISTING_INSTALL"

    if [ "$DRY_RUN" = true ]; then
        echo "$MSG_INSTALL_ABORT"
        echo "$MSG_USE_UPDATE"
    else
        echo "$MSG_INSTALL_ABORT" >&2
        echo "$MSG_USE_UPDATE" >&2
        exit 1
    fi
else
    echo
    echo "$MSG_FRESH_INSTALL"
fi

# =========================================================
# PORTOK
# =========================================================

echo
echo "$MSG_PORTS"

DB_PORT="$(
    find_free_port \
        "$DB_PORT_START" \
        "$DB_PORT_END"
)" || {
    echo "$MSG_PORT_ERROR" >&2
    exit 1
}

APP_PORT="$(
    find_free_port \
        "$APP_PORT_START" \
        "$APP_PORT_END"
)" || {
    echo "$MSG_PORT_ERROR" >&2
    exit 1
}


# =========================================================
# TELEPÍTÉSI TERV
# =========================================================

echo
echo "========================================"
echo "$MSG_PLAN"
echo "========================================"

printf "%-24s %s\n" \
    "$MSG_INSTALL_DIR:" \
    "$INSTALL_DIR"

printf "%-24s %s\n" \
    "$MSG_DB_PORT:" \
    "$DB_PORT"

printf "%-24s %s\n" \
    "$MSG_APP_PORT:" \
    "$APP_PORT"

echo


# =========================================================
# DRY RUN VÉGE
# =========================================================

if [ "$DRY_RUN" = true ]; then
    echo "$MSG_DRY_DONE"
    exit 0
fi


# =========================================================
# VALÓDI TELEPÍTÉS
# =========================================================

echo
echo "$MSG_START"


# ---------------------------------------------------------
# ROOT ELLENŐRZÉS
# ---------------------------------------------------------

if [
    "$(id -u)"
    -ne 0
]; then
    echo "$MSG_ROOT" >&2
    exit 1
fi


# ---------------------------------------------------------
# SYSTEM USER
# ---------------------------------------------------------

echo
echo "$MSG_CREATE_USER"

if ! id \
    symptomtracker \
    >/dev/null 2>&1
then
    useradd \
        --system \
        --home "$INSTALL_DIR" \
        --shell /usr/sbin/nologin \
        symptomtracker
fi


# ---------------------------------------------------------
# TELEPÍTÉSI KÖNYVTÁR
# ---------------------------------------------------------

echo
echo "$MSG_COPY_FILES"

mkdir -p \
    "$INSTALL_DIR"

if [
    "$PROJECT_DIR"
    != "$INSTALL_DIR"
]; then
    tar \
        --exclude='.git' \
        --exclude='.env' \
        --exclude='venv' \
        --exclude='backups' \
        --exclude='uploads/*' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        -C "$PROJECT_DIR" \
        -cf - \
        . \
    | tar \
        -C "$INSTALL_DIR" \
        -xf -
fi

mkdir -p \
    "$INSTALL_DIR/uploads/foods" \
    "$INSTALL_DIR/uploads/symptoms" \
    "$INSTALL_DIR/.gunicorn" \
    "$INSTALL_DIR/backups"


# ---------------------------------------------------------
# TITKOK
# ---------------------------------------------------------

echo
echo "$MSG_GENERATE_SECRETS"

DB_PASSWORD="$(
    generate_hex_secret 32
)"

SECRET_KEY="$(
    generate_hex_secret 48
)"


# ---------------------------------------------------------
# .ENV
# ---------------------------------------------------------

echo
echo "$MSG_WRITE_ENV"

umask 027

cat > "${INSTALL_DIR}/.env" <<EOF
DATABASE_URL=postgresql://symptomtracker_user:${DB_PASSWORD}@127.0.0.1:${DB_PORT}/symptomtracker
SECRET_KEY=${SECRET_KEY}

APP_PORT=${APP_PORT}
DB_PORT=${DB_PORT}

SYMPTOMTRACKER_DB_PASSWORD=${DB_PASSWORD}
EOF

chown \
    root:symptomtracker \
    "${INSTALL_DIR}/.env"

chmod 640 \
    "${INSTALL_DIR}/.env"


# ---------------------------------------------------------
# FÁJLJOGOSULTSÁGOK
# ---------------------------------------------------------

chown -R \
    root:root \
    "${INSTALL_DIR}/app" \
    "${INSTALL_DIR}/migrations" \
    "${INSTALL_DIR}/scripts" \
    "${INSTALL_DIR}/seed" \
    "${INSTALL_DIR}/installer"

chown \
    root:root \
    "${INSTALL_DIR}/run.py" \
    "${INSTALL_DIR}/config.py" \
    "${INSTALL_DIR}/requirements.txt" \
    "${INSTALL_DIR}/docker-compose.yml"

chown -R \
    symptomtracker:symptomtracker \
    "${INSTALL_DIR}/uploads" \
    "${INSTALL_DIR}/.gunicorn" \
    "${INSTALL_DIR}/backups"

chmod 750 \
    "${INSTALL_DIR}/uploads" \
    "${INSTALL_DIR}/uploads/foods" \
    "${INSTALL_DIR}/uploads/symptoms" \
    "${INSTALL_DIR}/.gunicorn" \
    "${INSTALL_DIR}/backups"


# ---------------------------------------------------------
# POSTGRESQL
# ---------------------------------------------------------

echo
echo "$MSG_START_DB"

cd "$INSTALL_DIR"

docker compose \
    --env-file "${INSTALL_DIR}/.env" \
    -f "${INSTALL_DIR}/docker-compose.yml" \
    up \
    -d \
    db


echo
echo "$MSG_WAIT_DB"

if ! wait_for_container_health \
    symptomtracker-db \
    30 \
    2
then
    echo "$MSG_DB_FAILED" >&2

    docker compose \
        --env-file "${INSTALL_DIR}/.env" \
        -f "${INSTALL_DIR}/docker-compose.yml" \
        logs \
        --tail=100 \
        db \
        >&2 \
        || true

    exit 1
fi

echo "$MSG_DB_READY"


# ---------------------------------------------------------
# ELSŐ SZAKASZ KÉSZ
# ---------------------------------------------------------

echo
echo "$MSG_PHASE1_DONE"

echo
printf "%-24s %s\n" \
    "$MSG_DB_PORT:" \
    "$DB_PORT"

printf "%-24s %s\n" \
    "$MSG_APP_PORT:" \
    "$APP_PORT"

# ---------------------------------------------------------
# PYTHON VENV
# ---------------------------------------------------------

echo
echo "$MSG_CREATE_VENV"

if [ ! -x "${INSTALL_DIR}/venv/bin/python" ]; then
    python3 -m venv \
        "${INSTALL_DIR}/venv"
fi


# ---------------------------------------------------------
# REQUIREMENTS
# ---------------------------------------------------------

echo
echo "$MSG_INSTALL_REQUIREMENTS"

"${INSTALL_DIR}/venv/bin/python" \
    -m pip install \
    --upgrade pip

"${INSTALL_DIR}/venv/bin/pip" \
    install \
    -r "${INSTALL_DIR}/requirements.txt"


# ---------------------------------------------------------
# MIGRÁCIÓ
# ---------------------------------------------------------

echo
echo "$MSG_RUN_MIGRATIONS"

set -a
# shellcheck source=/dev/null
source "${INSTALL_DIR}/.env"
set +a

FLASK_SKIP_DOTENV=1 \
DATABASE_URL="$DATABASE_URL" \
PYTHONDONTWRITEBYTECODE=1 \
"${INSTALL_DIR}/venv/bin/flask" \
    --app app:create_app \
    db upgrade


# ---------------------------------------------------------
# REFERENCE SEED
# ---------------------------------------------------------

echo
echo "$MSG_IMPORT_SEED"

DATABASE_URL="$DATABASE_URL" \
PYTHONDONTWRITEBYTECODE=1 \
"${INSTALL_DIR}/venv/bin/python" \
    "${INSTALL_DIR}/scripts/import_reference_seed.py"


# ---------------------------------------------------------
# MÁSODIK SZAKASZ KÉSZ
# ---------------------------------------------------------

echo
echo "$MSG_PHASE2_DONE"

exit 0
