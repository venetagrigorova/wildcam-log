# Wildcam log

A small web app for NERDS uc that logs which animal was visible when in which live stream.
Built with Flask and PostgreSQL, packaged as a Docker container.

## Run locally

Requires Docker Desktop.

```
docker compose up --build
```

Then open http://localhost:8000 for land and air animals and http://localhost:8001 for sea animals. Stop with Ctrl+C.

## Configuration

The app reads three environment variables:

| Variable | Example |
|---|---|
| `APP_TYPE` | `lair` (land and air animals) or `sea` (sea animals), required |
| `HOST` | `worker1` (shown on the page as "Served by") |
| `DATABASE_URL` | `postgresql://postgres:PASSWORD@192.168.100.101:5432/wildcam` |

The table and its `type` column are created automatically on start.
Sightings logged before the `type` column existed have no type, so neither container shows them until one is set.

## Routing

The ingress sends `/lair` to the `lair` container and `/sea` to the `sea` container.
The app works whether or not the ingress strips that prefix.

## Run on a worker VM

```
docker build -t wildcam .
docker run -d --name wildcam-lair --restart always -p 8000:8000 \
  -e APP_TYPE=lair \
  -e HOST="$(hostname)" \
  -e DATABASE_URL=postgresql://postgres:PASSWORD@192.168.100.101:5432/wildcam \
  wildcam
docker run -d --name wildcam-sea --restart always -p 8001:8000 \
  -e APP_TYPE=sea \
  -e HOST="$(hostname)" \
  -e DATABASE_URL=postgresql://postgres:PASSWORD@192.168.100.101:5432/wildcam \
  wildcam
```

The top of the page shows which worker served the request, which makes load balancing visible.
