#!/usr/bin/env bash


port_is_free() {
    local port="$1"

    python3 - "$port" <<'PY'
import socket
import sys


port = int(
    sys.argv[1]
)

sock = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM,
)

try:
    sock.bind(
        (
            "127.0.0.1",
            port,
        )
    )

except OSError:
    raise SystemExit(1)

finally:
    sock.close()

raise SystemExit(0)
PY
}


find_free_port() {
    local start_port="$1"
    local max_port="$2"
    local port="$start_port"

    while [ "$port" -le "$max_port" ]; do
        if port_is_free "$port"; then
            echo "$port"
            return 0
        fi

        port=$((port + 1))
    done

    return 1
}

generate_hex_secret() {
    local bytes="${1:-32}"

    python3 - "$bytes" <<'PY'
import secrets
import sys

byte_count = int(
    sys.argv[1]
)

print(
    secrets.token_hex(
        byte_count
    )
)
PY
}


wait_for_container_health() {
    local container_name="$1"
    local max_attempts="${2:-30}"
    local sleep_seconds="${3:-2}"
    local attempt=1

    while [ "$attempt" -le "$max_attempts" ]; do
        local status

        status="$(
            docker inspect \
                --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' \
                "$container_name" \
                2>/dev/null \
                || true
        )"

        if [ "$status" = "healthy" ]; then
            return 0
        fi

        if [ "$status" = "unhealthy" ]; then
            return 1
        fi

        sleep "$sleep_seconds"

        attempt=$((attempt + 1))
    done

    return 1
}

wait_for_http() {
    local url="$1"
    local max_attempts="${2:-30}"
    local sleep_seconds="${3:-2}"
    local attempt=1

    while [ "$attempt" -le "$max_attempts" ]; do
        if python3 - "$url" <<'PY'
import sys
import urllib.request

url = sys.argv[1]

try:
    with urllib.request.urlopen(
        url,
        timeout=3,
    ) as response:
        status = response.status

except Exception:
    raise SystemExit(1)

if 200 <= status < 400:
    raise SystemExit(0)

raise SystemExit(1)
PY
        then
            return 0
        fi

        sleep "$sleep_seconds"
        attempt=$((attempt + 1))
    done

    return 1
}
