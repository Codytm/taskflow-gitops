# TaskFlow GitOps

A small task app for learning how a code change becomes a running service.

The goal is a full path from a git push to a Kubernetes cluster: GitHub Actions builds the images, and Argo CD makes the cluster match what is in git.

## Stack

- API: FastAPI
- Web: React and Vite
- Database: PostgreSQL
- Local run: Docker Compose
- Later: Kind, Kustomize, GitHub Container Registry, and Argo CD

## Run locally

docker compose up --build

- Web: http://localhost:5173
- API: http://localhost:8000
