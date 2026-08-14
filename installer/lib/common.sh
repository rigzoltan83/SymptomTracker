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
