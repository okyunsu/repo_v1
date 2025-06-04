@echo off

echo 🧹 Cleaning up k3d cluster and resources...

REM Delete k3d cluster
echo 🗑️ Deleting k3d cluster...
k3d cluster delete modorepo-cluster

REM Remove Docker images (optional)
set /p choice="Do you want to remove the Docker image? (y/N): "
if /i "%choice%"=="y" (
    echo 🗑️ Removing Docker image...
    docker rmi lif-app:latest 2>nul || echo Image not found or already removed
)

echo ✅ Cleanup completed!
pause 