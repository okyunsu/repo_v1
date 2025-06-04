@echo off
echo ========================================
echo 🚀 Full-Stack k3d 배포 시작
echo ========================================

REM 현재 디렉토리 확인
echo 📁 현재 디렉토리: %CD%

REM 1. 백엔드 Docker 이미지 빌드
echo.
echo 🔨 백엔드 이미지 빌드 중...
docker build -t lif-app:latest .
if %ERRORLEVEL% neq 0 (
    echo ❌ 백엔드 이미지 빌드 실패
    exit /b 1
)

REM 2. 프론트엔드 Docker 이미지 빌드
echo.
echo 🔨 프론트엔드 이미지 빌드 중...
cd frontend
docker build -t lif-frontend:latest .
if %ERRORLEVEL% neq 0 (
    echo ❌ 프론트엔드 이미지 빌드 실패
    exit /b 1
)
cd ..

REM 3. 이미지를 k3d 클러스터로 가져오기
echo.
echo 📦 이미지를 k3d 클러스터로 가져오는 중...
k3d image import lif-app:latest -c modorepo-cluster
k3d image import lif-frontend:latest -c modorepo-cluster

REM 4. 네임스페이스 생성
echo.
echo 🏗️ 네임스페이스 생성 중...
kubectl apply -f k8s/namespace.yaml

REM 5. ConfigMap 생성
echo.
echo ⚙️ ConfigMap 생성 중...
kubectl apply -f k8s/app-configmap.yaml

REM 6. PostgreSQL 배포
echo.
echo 🗄️ PostgreSQL 배포 중...
kubectl apply -f k8s/postgres-configmap.yaml
kubectl apply -f k8s/postgres-pvc.yaml
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/postgres-service.yaml

REM PostgreSQL 준비 대기
echo.
echo ⏳ PostgreSQL 준비 대기 중...
kubectl wait --for=condition=Available deployment/postgres -n lif-system --timeout=300s
if %ERRORLEVEL% neq 0 (
    echo ❌ PostgreSQL 배포 실패
    exit /b 1
)

REM 7. 백엔드 애플리케이션 배포
echo.
echo 🚀 백엔드 애플리케이션 배포 중...
kubectl apply -f k8s/app-deployment.yaml
kubectl apply -f k8s/app-service.yaml
kubectl apply -f k8s/app-hpa.yaml

REM 8. 프론트엔드 애플리케이션 배포
echo.
echo 🎨 프론트엔드 애플리케이션 배포 중...
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml
kubectl apply -f k8s/frontend-hpa.yaml

REM 9. Ingress 설정
echo.
echo 🌐 Ingress 설정 중...
kubectl apply -f k8s/ingress.yaml

REM 10. 배포 상태 확인
echo.
echo 📊 배포 상태 확인 중...
echo.
echo === 파드 상태 ===
kubectl get pods -n lif-system
echo.
echo === 서비스 상태 ===
kubectl get svc -n lif-system
echo.
echo === HPA 상태 ===
kubectl get hpa -n lif-system

echo.
echo ========================================
echo ✅ Full-Stack 배포 완료!
echo ========================================
echo.
echo 🌐 접속 정보 (모든 서비스가 8080 포트로 통합):
echo   - 프론트엔드 메인: http://localhost:8080
echo   - 백엔드 API 문서: http://localhost:8080/docs
echo   - 백엔드 ReDoc: http://localhost:8080/redoc
echo   - 헬스 체크: http://localhost:8080/health
echo.
echo 🔍 각 백엔드 서비스 엔드포인트:
echo   - Finance Service: http://localhost:8080/finance
echo   - Stock Service: http://localhost:8080/stock
echo   - ESG Service: http://localhost:8080/esg
echo   - Ratio Service: http://localhost:8080/ratio
echo   - News Service: http://localhost:8080/news
echo   - PDF Service: http://localhost:8080/pdf
echo.
echo 📊 모니터링:
echo   kubectl get pods -n lif-system
echo   kubectl get hpa -n lif-system
echo   kubectl logs -f deployment/lif-frontend -n lif-system
echo   kubectl logs -f deployment/lif-app -n lif-system
echo.
pause 