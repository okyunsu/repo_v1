@echo off
echo Building Docker image...
docker build -t lif-app:latest .

echo Importing image to k3d cluster...
k3d image import lif-app:latest -c modorepo-cluster

echo Deleting existing deployment...
kubectl delete deployment lif-app -n lif-system

echo Applying updated deployment...
kubectl apply -f k8s/app-deployment.yaml

echo Waiting for pods to be ready...
kubectl wait --for=condition=ready pod -l app=lif-app -n lif-system --timeout=300s

echo Checking pod status...
kubectl get pods -n lif-system

echo Done! 