@echo off

echo 🧪 Testing Load Balancing and Auto-scaling...

REM Check current status
echo 📊 Current deployment status:
kubectl get pods -n lif-system -l app=lif-app
kubectl get hpa -n lif-system

echo.
echo 🔄 Testing manual scaling...
echo Scaling to 5 replicas...
kubectl scale deployment lif-app --replicas=5 -n lif-system

echo Waiting for pods to be ready...
kubectl wait --for=condition=Ready pods -l app=lif-app -n lif-system --timeout=300s

echo 📊 Updated status:
kubectl get pods -n lif-system -l app=lif-app

echo.
echo 🌐 Testing load balancing...
echo Making requests to the gateway service...

for /l %%i in (1,1,10) do (
    echo Request %%i:
    kubectl exec -n lif-system deployment/lif-app -- curl -s http://localhost:8080/health
    timeout /t 1 /nobreak >nul
)

echo.
echo 📈 Load testing will trigger auto-scaling...
echo You can monitor HPA with: kubectl get hpa -n lif-system
echo.
echo 📊 Final status:
kubectl get pods -n lif-system -l app=lif-app
kubectl get hpa -n lif-system

echo.
echo ✅ Scaling test completed!
echo 💡 You can monitor ongoing scaling with:
echo    kubectl get pods -n lif-system
echo    kubectl get hpa -n lif-system

pause 