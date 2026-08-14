#!/usr/bin/env python3

import os
import sys
import time

import psycopg2


database_url = os.environ.get(
    "DATABASE_URL"
)

if not database_url:
    print(
        "DATABASE_URL is not set.",
        file=sys.stderr,
    )
    raise SystemExit(1)


max_attempts = 60
sleep_seconds = 2

for attempt in range(
    1,
    max_attempts + 1,
):
    try:
        connection = psycopg2.connect(
            database_url,
            connect_timeout=3,
        )

        connection.close()

        print(
            "Database is ready."
        )

        raise SystemExit(0)

    except psycopg2.Error as exc:
        if attempt == max_attempts:
            print(
                "Database did not become ready:",
                exc,
                file=sys.stderr,
            )

            raise SystemExit(1)

        time.sleep(
            sleep_seconds
        )
