@echo off
setlocal enabledelayedexpansion

echo 🚀 Starting k3d deployment for LIF Backend Services...

REM Check if k3d is installed
k3d version >nul 2>&1
if errorlevel 1 (
    echo ❌ k3d is not installed. Please install k3d first.
    echo Visit: https://k3d.io/v5.4.6/#installation
    exit /b 1
)

REM Check if kubectl is installed
kubectl version --client >nul 2>&1
if errorlevel 1 (
    echo ❌ kubectl is not installed. Please install kubectl first.
    exit /b 1
)

REM Check if cluster exists, if not create it
k3d cluster list | findstr "modorepo-cluster" >nul
if errorlevel 1 (
    echo 📦 Creating k3d cluster...
    k3d cluster create modorepo-cluster -p "8080:80@loadbalancer" --agents 1
) else (
    echo 📦 Using existing k3d cluster: modorepo-cluster
    k3d cluster start modorepo-cluster 2>nul || echo Cluster already running
)

REM Wait for cluster to be ready
echo ⏳ Waiting for cluster to be ready...
kubectl wait --for=condition=Ready nodes --all --timeout=300s

REM Build Docker image
echo 🔨 Building Docker image...
docker build -t lif-app:latest .

REM Import image to k3d cluster
echo 📥 Importing image to k3d cluster...
k3d image import lif-app:latest -c modorepo-cluster

REM Apply Kubernetes manifests
echo 🚀 Deploying to Kubernetes...

REM Apply in order
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/postgres-configmap.yaml
kubectl apply -f k8s/postgres-pvc.yaml
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/postgres-service.yaml

REM Wait for PostgreSQL to be ready
echo ⏳ Waiting for PostgreSQL to be ready...
kubectl wait --for=condition=Available deployment/postgres -n lif-system --timeout=300s

REM Apply application resources
kubectl apply -f k8s/app-deployment.yaml
kubectl apply -f k8s/app-service.yaml
kubectl apply -f k8s/app-hpa.yaml

REM Wait for application to be ready
echo ⏳ Waiting for application to be ready...
kubectl wait --for=condition=Available deployment/lif-app -n lif-system --timeout=600s

echo ✅ Deployment completed successfully!
echo.
echo 🌐 Access your backend services:
echo    API Gateway: http://localhost:8080
echo    Finance Service: http://localhost:8080/finance
echo    Stock Service: http://localhost:8080/stock
echo    ESG Service: http://localhost:8080/esg
echo    Ratio Service: http://localhost:8080/ratio
echo    News Service: http://localhost:8080/news
echo    PDF Service: http://localhost:8080/pdf
echo.
echo 📊 Monitor your deployment:
echo    kubectl get pods -n lif-system
echo    kubectl get hpa -n lif-system
echo    kubectl logs -f deployment/lif-app -n lif-system
echo.
echo 🔧 Scale your application:
echo    kubectl scale deployment lif-app --replicas=5 -n lif-system

pause 