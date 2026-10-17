import os
import socket

import psycopg
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)

# Database connection settings come from environment variables,
# so the same container works locally and on the worker VMs.
DB_URL = os.environ.get(
    "DATABASE_URL", "postgresql://wildcam:wildcam@localhost:5432/wildcam"
)


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


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        animal = request.form.get("animal", "").strip()
        stream = request.form.get("stream", "").strip()
        seen_at = request.form.get("seen_at", "").strip()
        if animal and stream and seen_at:
            with get_conn() as conn:
                conn.execute(
                    "INSERT INTO sightings (animal, stream, seen_at) VALUES (%s, %s, %s)",
                    (animal, stream, seen_at),
                )
        return redirect(url_for("index"))

    with get_conn() as conn:
        rows = conn.execute(
            "SELECT animal, stream, seen_at FROM sightings ORDER BY seen_at DESC"
        ).fetchall()

    # The hostname shows which worker answered, handy for proving
    # the load balancer spreads requests across all three.
    return render_template("index.html", rows=rows, host=socket.gethostname())


@app.route("/health")
def health():
    return "ok"


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
