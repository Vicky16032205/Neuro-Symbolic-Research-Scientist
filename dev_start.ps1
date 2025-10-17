# dev_start.ps1 — build and start the Docker Compose stack
Write-Output "Building and starting Docker Compose stack..."
docker compose up --build -d
Write-Output "Use 'docker compose ps' to inspect running containers, or open http://localhost:8501 for the dashboard."
