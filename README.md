# Wildcam log

A small web app for NERDS uc that logs which animal was visible when in which live stream.
Built with Flask and PostgreSQL, packaged as a Docker container.

## Run locally

Requires Docker Desktop.

```
docker compose up --build
```

Then open http://localhost:8000. Stop with Ctrl+C.

## Configuration

The app reads two environment variables:

| Variable | Example |
|---|---|
| `HOST` | `worker1` (shown on the page as "Served by") |
| `DATABASE_URL` | `postgresql://postgres:PASSWORD@192.168.100.101:5432/wildcam` |

The table is created automatically on first start.

## Run on a worker VM

```
docker build -t wildcam .
docker run -d --name wildcam --restart always -p 8000:8000 \
  -e HOST="$(hostname)" \
  -e DATABASE_URL=postgresql://postgres:PASSWORD@192.168.100.101:5432/wildcam \
  wildcam
```

The top of the page shows which worker served the request, which makes load balancing visible.
