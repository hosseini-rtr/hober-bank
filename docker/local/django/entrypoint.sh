#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset 

python <<END
import sys
import time
import psycopg2
import os

suggest_unrecoverable_after = 5
start = time.time()

while True:
    try:
        psycopg2.connect(
            dbname=os.environ["POSTGRES_DB"],
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
            host=os.environ["POSTGRES_HOST"],
            port=os.environ["POSTGRES_PORT"],
        )
        print(f"Connected to {os.environ['POSTGRES_DB']} as {os.environ['POSTGRES_USER']}")
        break
    except psycopg2.OperationalError as e:
        sys.stderr.write(f" ** waiting for PSQL to be available ** {time.time() - start} \n")
        if time.time() - start > suggest_unrecoverable_after:
            sys.stderr.write(f"This is taking longer than expected. The following exception indicative of an unrecoverable error:{e} \n ")
        time.sleep(3)
END

echo >&2 'PostgreSQL is available'

exec "$@"
