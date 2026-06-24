# sample-app — CI/CD Pipeline on AWS EC2

A tiny Flask web application wired into a fully automated CI/CD pipeline. Every push to `main` runs tests, builds a Docker image, publishes it to Docker Hub, and deploys it to an AWS EC2 instance — no manual steps.

---

## Overview

```
GitHub push ─▶ GitHub Actions ─▶ Docker Hub ─▶ EC2 (Docker)
              (test → build → deploy)
```

| Stage | What it does |
|-------|--------------|
| **test** | Runs `pytest` so a broken commit never ships |
| **build-and-push** | Builds the Docker image and pushes it to Docker Hub |
| **deploy** | SSHes into EC2, pulls the new image, restarts the container |

The three jobs run in sequence via `needs:`, so each stage only proceeds if the previous one passed.

---

## Tech Stack

- **App:** Python 3.12 · Flask 3.0.3
- **Tests:** pytest 8.2.0
- **Containerization:** Docker
- **CI/CD:** GitHub Actions
- **Registry:** Docker Hub
- **Host:** AWS EC2 (Ubuntu Server 24.04 LTS)

---

## Project Structure

```
sample-app/
├── app.py                    # Flask app: home page + /health endpoint
├── requirements.txt          # Python dependencies
├── test_app.py               # Tests run automatically by the pipeline
├── Dockerfile                # Recipe to package the app into an image
└── .github/
    └── workflows/
        └── ci-cd.yml         # The CI/CD pipeline definition
```

---

## Prerequisites

- An AWS account (free-tier eligible)
- A GitHub account
- A Docker Hub account
- An SSH client (e.g. MobaXterm) with your `devops-key.pem`

---

## Application

The app exposes two routes:

| Route | Method | Response |
|-------|--------|----------|
| `/` | GET | `Hello from the CI/CD pipeline! Version 1.0` |
| `/health` | GET | `{"status": "healthy"}` (HTTP 200) |

It listens on `0.0.0.0:5000`.

---

## Infrastructure Setup (AWS EC2)

1. Launch an EC2 instance — Ubuntu Server 24.04 LTS, `t2.micro` (or `t3.small` if running the observability stack).
2. Create an RSA key pair named `devops-key` (`.pem`) and keep it safe.
3. Configure the security group inbound rules (below).
4. Copy the instance's **Public IPv4 address**.

### Security Group — Inbound Rules

| Port | Used by | Source |
|------|---------|--------|
| 22 | SSH | My IP |
| 5000 | Sample web app | My IP / 0.0.0.0/0 |
| 3000 | Grafana | My IP |
| 9090 | Prometheus | My IP |
| 16686 | Jaeger UI | My IP |

### Install Docker & Git on the server

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git docker.io docker-compose-v2
sudo systemctl enable --now docker
sudo usermod -aG docker $USER   # log out/in (or run: newgrp docker)
```

Verify:

```bash
docker --version
docker compose version
git --version
docker run hello-world
```

---

## Run Locally (on the server)

```bash
docker build -t sample-app .
docker run -d -p 5000:5000 --name sample-app sample-app
curl localhost:5000          # -> Hello from the CI/CD pipeline!
```

Open `http://<EC2-PUBLIC-IP>:5000` in a browser. Then clean up so the pipeline can take over:

```bash
docker rm -f sample-app
```

---

## GitHub Secrets

In the repo: **Settings → Secrets and variables → Actions → New repository secret**. Add all five:

| Secret name | Value |
|-------------|-------|
| `DOCKERHUB_USERNAME` | Your Docker Hub username |
| `DOCKERHUB_TOKEN` | Docker Hub access token |
| `EC2_HOST` | EC2 public IPv4 address |
| `EC2_USER` | `ubuntu` |
| `EC2_SSH_KEY` | The entire contents of `devops-key.pem` |

> ⚠️ **Never** commit `devops-key.pem` or your Docker Hub token to the repository. Secrets are encrypted and never printed in logs.

---

## Deploy

Push any change to `main` and the pipeline runs automatically:

```bash
git add .
git commit -m "Trigger pipeline"
git push
```

Then:

1. Open the repo's **Actions** tab and watch the three jobs turn green in sequence.
2. Confirm the new image appears on **Docker Hub**.
3. Visit `http://<EC2-PUBLIC-IP>:5000` — the new version is live, deployed automatically.

---

## Notes

- GitHub no longer accepts your account password over HTTPS. When prompted for a password during `git push`, paste a **Personal Access Token** (GitHub → Settings → Developer settings → Tokens) with the `repo` scope.
- `|| true` in the deploy step stops the workflow from failing on the first run when no old container exists yet.

---

## License

MIT (or your choice).
