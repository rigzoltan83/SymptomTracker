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
            "0.0.0.0",
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

install_docker_ubuntu() {
    apt-get update

    apt-get install -y \
        ca-certificates \
        curl

    install \
        -m 0755 \
        -d \
        /etc/apt/keyrings

    curl \
        -fsSL \
        https://download.docker.com/linux/ubuntu/gpg \
        -o /etc/apt/keyrings/docker.asc

    chmod a+r \
        /etc/apt/keyrings/docker.asc

    cat > /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: ${UBUNTU_CODENAME:-$VERSION_CODENAME}
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF

    apt-get update

    apt-get install -y \
        docker-ce \
        docker-ce-cli \
        containerd.io \
        docker-buildx-plugin \
        docker-compose-plugin

    systemctl enable \
        --now \
        docker
}

package_is_installed() {
    local package="$1"

    dpkg-query \
        -W \
        -f='${Status}' \
        "$package" \
        2>/dev/null \
        | grep -Fq \
            'install ok installed'
}


ensure_docker_compose() {
    if docker compose version \
        >/dev/null 2>&1
    then
        return 0
    fi

    echo "$MSG_COMPOSE_MISSING"

    if package_is_installed docker-ce; then
        echo "$MSG_DOCKER_CE_FOUND"
        echo "$MSG_INSTALL_COMPOSE"

        apt-get update

        apt-get install -y \
            docker-compose-plugin

    elif package_is_installed docker.io; then
        echo "$MSG_DOCKER_IO_FOUND"
        echo "$MSG_INSTALL_COMPOSE"

        apt-get update

        apt-get install -y \
            docker-compose-v2

    else
        echo "$MSG_DOCKER_UNKNOWN" >&2
        echo "$MSG_DOCKER_UNKNOWN_ABORT" >&2

        return 1
    fi

    docker compose version \
        >/dev/null 2>&1
}
