# dev_stop.ps1 — stop and remove the Docker Compose stack
Write-Output "Stopping and removing Docker Compose stack..."
docker compose down
Write-Output "Stopped."
