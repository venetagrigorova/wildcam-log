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

The app reads one environment variable:

| Variable | Example |
|---|---|
| `DATABASE_URL` | `postgresql://wildcam:PASSWORD@192.168.100.10:5432/wildcam` |

The table is created automatically on first start.

## Run on a worker VM

```
docker build -t wildcam .
docker run -d --name wildcam --restart unless-stopped -p 8000:8000 \
  -e DATABASE_URL=postgresql://wildcam:PASSWORD@192.168.100.10:5432/wildcam \
  wildcam
```

The page footer shows which worker served the request, which makes load balancing visible.
