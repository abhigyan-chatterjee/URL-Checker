# Deploying to urlcheck.nullbit.in (Oracle Free Tier + Docker + Caddy)

## 1. Create the VM (Oracle Cloud Free Tier)

- **Shape:** `VM.Standard.A1.Flex` (Ampere ARM64) — 1 OCPU, 6 GB RAM. Must be Ampere; the free AMD `E2.1.Micro` (1 GB) will OOM on torch.
- **Image:** Ubuntu 24.04 (aarch64)
- **Networking:** public IPv4 assigned; keep the default VCN/public subnet
- **Security list:** allow ingress on TCP **80** and **443** (SSH/22 is already open)

> Cheapest region availability for A1 shapes varies — any home region works.

## 2. DNS (Cloudflare)

Add an **A record**: `urlcheck.nullbit.in` → VPS public IP.
- DNS-only (grey cloud): simplest, Caddy gets its own Let's Encrypt cert.
- Proxied (orange cloud): also fine — set SSL/TLS mode to **Full (strict)**; Caddy still terminates with a real LE cert at the origin.

## 3. Provision the VPS

```bash
sudo apt update && sudo apt install -y docker.io docker-compose-v2
sudo usermod -aG docker $USER   # log out/in after this

# Oracle Ubuntu images REJECT non-SSH traffic in iptables by default:
sudo iptables -I INPUT -p tcp -m multiport --dports 80,443 -j ACCEPT

git clone https://github.com/abhigyan-chatterjee/URL-Checker.git
cd URL-Checker
docker compose up -d --build
```

App runs on `127.0.0.1:8501` (loopback only — not exposed to the internet directly).

## 4. Caddy (TLS + proxy)

```bash
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update && sudo apt install -y caddy

sudo cp ~/URL-Checker/Caddyfile /etc/caddy/Caddyfile
sudo systemctl reload caddy
```

Caddy obtains the TLS cert automatically. Visit https://urlcheck.nullbit.in

## Maintenance

```bash
cd ~/URL-Checker
git pull && docker compose up -d --build   # deploy updates
docker logs -f urlcheck                    # logs
```

First `docker compose up --build` on 1 OCPU takes ~5 min (pip downloads ~400 MB of wheels).
Runtime memory: ~600–900 MB (torch + streamlit) — comfortable on 6 GB.
