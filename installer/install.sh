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
echo
echo "The installation phase is not enabled yet."
echo "Use --dry-run."
exit 1
