0.1 Launch the EC2 instance
1. Sign in to the AWS Console → search EC2 → click Launch instance.
2. Name: devops-lab.
3. AMI: Ubuntu Server 24.04 LTS (free-tier eligible).
4. Instance type: t2.micro (free tier). For the observability stack a t2.small / t3.small is smoother because six containers run at once.
5. Key pair: Create new → name devops-key → type RSA → format .pem → download and keep it safe. This file is how MobaXterm proves who you are.
6. Network / Security group: add inbound rules (see table below).
7. Click Launch instance, then copy the Public IPv4 address from the instance page.

Port Used by Source
22 SSH (MobaXterm) My IP
5000 Sample web app My IP / 0.0.0.0/0
3000 Grafana (Project 3) My IP
9090 Prometheus (Project 3) My IP
16686 Jaeger UI (Project 3) My IP


0.2 Connect with MobaXterm
1. Open MobaXterm → Session → SSH.
2. Remote host: your EC2 Public IPv4.
3. Tick Specify username and enter ubuntu.
4. Expand Advanced SSH settings → tick Use private key → browse to devops-key.pem.
5. Click OK. MobaXterm opens a terminal and a left-side file browser (handy for editing config files).
NOTE On the very first connect MobaXterm asks to accept the host key — click Accept. The left file panel lets you drag-and-drop files between your laptop and the server.
0.3 Install Docker & Git on the server
Run these once in the MobaXterm terminal:
BASH
sudo apt update && sudo apt upgrade -y
sudo apt install -y git docker.io docker-compose-v2
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
WHY The last line adds your user to the reconnect (or run newgrp docker ).
docker group so you can run docker without sudo. It only takes effect on a new session — close the MobaXterm tab and
Verify everything is ready:
BASH
docker --version
docker compose version
git --version
docker run hello-world # prints a success message and exits
Step 1 Create the sample application
On the EC2 server, create a project folder and four files. (You can use MobaXterm’s left file panel or nano.)
mkdir ~/sample-app && cd ~/sample-app
app.py — a tiny Flask web app with a home page and a health-check endpoint:
from flask import Flask
app = Flask(__
name
__)
@app.route("/")
def home():
return "Hello from the CI/CD pipeline! Version 1.0"
@app.route("/health")
def health():
return {"status": "healthy"}, 200
if
name
== "
main
":
__
__
__
__
app.run(host="0.0.0.0"
, port=5000)
requirements.txt — Python dependencies:
flask==3.0.3
pytest==8.2.0
test
_
app.py — the tests the pipeline will run automatically:
from app import app
def test
home():
_
res = app.test
_
client().get("/")
assert res.status
code == 200
_
assert b"Hello" in res.data
def test
health():
_
res = app.test
_
client().get("/health")
assert res.status
code == 200
_
Dockerfile — the recipe that packages the app into an image:
BASH
PYTHON
TEXT
PYTHON
DOCKERFILE
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python"
,
"app.py"]
WHY 5000, and define the start command.
Each Dockerfile line is one step: pick a base image, set the working folder, copy and install dependencies first (so Docker can cache that layer), copy the code, open port
Confirm it works locally before automating anything:
BASH
docker build -t sample-app .
docker run -d -p 5000:5000 --name sample-app sample-app
curl localhost:5000 # -> Hello from the CI/CD pipeline!
Open http://<EC2-PUBLIC-IP>:5000 in a browser to see it live. Then stop it so the pipeline can take over later: docker rm -f sample-app.
Step 2 Push the code to GitHub
Create an empty repo on GitHub (e.g. sample-app ), then from the server:
BASH
git init
git add .
git commit -m "Initial commit: Flask app + Dockerfile"
git branch -M main
git remote add origin https://github.com/<your-username>/sample-app.git
git push -u origin main
IMPORTANT settings → Tokens). Give it the repo scope.
GitHub no longer accepts your account password over HTTPS. When prompted for a password, paste a Personal Access Token (GitHub → Settings → Developer
Step 3 Prepare Docker Hub
1. Create a free account at hub.docker.com.
2. Go to Account Settings → Security → New Access Token, copy the token (you will store it as a secret).
Step 4 Add GitHub repository secrets
In the repo: Settings → Secrets and variables → Actions → New repository secret. Add these five:
Secret name Value
DOCKERHUB_USERNAME your Docker Hub username
DOCKERHUB_TOKEN  the Docker Hub access token
EC2_HOST EC2 public IPv4 address
EC2_USER ubuntu
EC2_SSH  KEY the entire contents of devops-key.pem

IMPORTANT Secrets are encrypted and never printed in logs. Never commit the .pem key or the Docker token into the repository itself.

Step 5 Write the pipeline

Create the file .github/workflow/ci-cd.yml


WHY The three jobs run in order because of pulls the new image and restarts the container. needs:. test guards the build (a broken commit never ships); build-and-push publishes the image; deploy SSHes into EC2,
|| true stops the workflow failing on the first run when no old container exists.
Step 6 Run and verify the pipeline
BASH
# make any change, e.g. edit the message in app.py, then:
git add .
git commit -m "Trigger pipeline"
git push
1. Open the repo’s Actions tab — watch the three jobs turn green in sequence.
2. Check the image appeared on Docker Hub.
3. Visit http://<EC2-PUBLIC-IP>:5000 — the new version is live, deployed automatically.









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
