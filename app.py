import os
import socket

import psycopg
from flask import Flask, redirect, render_template, request

app = Flask(__name__)

# Database connection settings come from environment variables,
# so the same container works locally and on the worker VMs.
DB_URL = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:password@db:5432/wildcam"
)

# Name of the worker VM, passed in with -e HOST=$(hostname) on docker run.
# Falls back to the container's own hostname if not set.
HOST = os.environ.get("HOST", socket.gethostname())

# Which part of the app this container serves, and the values of the
# "type" column that belong to it.
ANIMAL_TYPES_BY_APP_TYPE = {"lair": ["land", "air"], "sea": ["sea"]}

APP_TYPE = os.environ.get("APP_TYPE")
if APP_TYPE not in ANIMAL_TYPES_BY_APP_TYPE:
    raise RuntimeError("APP_TYPE must be set to 'lair' or 'sea'")

ANIMAL_TYPES = ANIMAL_TYPES_BY_APP_TYPE[APP_TYPE]

# The ingress sends /lair and /sea to the matching container.
BASE_PATH = f"/{APP_TYPE}"


def get_conn():
    return psycopg.connect(DB_URL)


def init_db():
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sightings (
                id SERIAL PRIMARY KEY,
                animal TEXT NOT NULL,
                stream TEXT NOT NULL,
                seen_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT now()
            )
            """
        )
        # Separate from CREATE TABLE so databases that already have the
        # table get the column too. Existing rows keep type NULL.
        conn.execute(
            """
            ALTER TABLE sightings ADD COLUMN IF NOT EXISTS
                type TEXT CHECK (type IN ('land', 'air', 'sea'))
            """
        )


# Both routes lead here so the app works whether or not the ingress strips
# the prefix. Redirects always use BASE_PATH, because "/" would leave the
# prefix and miss this container.
@app.route("/", methods=["GET", "POST"])
@app.route(BASE_PATH, methods=["GET", "POST"], strict_slashes=False)
def index():
    if request.method == "POST":
        animal = request.form.get("animal", "").strip()
        stream = request.form.get("stream", "").strip()
        seen_at = request.form.get("seen_at", "").strip()
        animal_type = request.form.get("type", "").strip()
        if animal and stream and seen_at and animal_type in ANIMAL_TYPES:
            with get_conn() as conn:
                conn.execute(
                    "INSERT INTO sightings (animal, stream, seen_at, type) VALUES (%s, %s, %s, %s)",
                    (animal, stream, seen_at, animal_type),
                )
        return redirect(BASE_PATH)

    with get_conn() as conn:
        rows = conn.execute(
            "SELECT animal, stream, seen_at, type FROM sightings WHERE type = ANY(%s) ORDER BY seen_at DESC",
            (ANIMAL_TYPES,),
        ).fetchall()

    # The hostname shows which worker answered, handy for proving
    # the load balancer spreads requests across all three.
    return render_template(
        "index.html",
        rows=rows,
        host=HOST,
        animal_types=ANIMAL_TYPES,
        heading=" and ".join(ANIMAL_TYPES),
    )


@app.route("/health")
def health():
    return "ok"


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
