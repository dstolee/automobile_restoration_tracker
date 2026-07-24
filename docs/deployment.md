# Deployment guide

## Docker Compose

Copy `.env.example` to `.env`, replace the secret, and run:

```bash
docker compose up -d --build
```

Open `http://SERVER-IP:5000`.

## Persistent data

The Compose configuration mounts `./data` into `/data`. Back up both:

- `data/restoration.db`
- `data/uploads/`

## Reverse proxy

For LAN-only use, direct port access is acceptable. For HTTPS, place the service behind Caddy, Nginx, or Traefik. Keep the app on a trusted VLAN and use a VPN for remote access.

## Updating

```bash
git pull
docker compose up -d --build
```

Back up persistent data before upgrades.

## Health check

The image exposes `/healthz`. A successful response is JSON with `status` set to `ok`.
