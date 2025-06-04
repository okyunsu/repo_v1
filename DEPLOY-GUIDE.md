# 🚀 k3d Full-Stack 배포 가이드 (Windows)

기존에 생성하신 `modorepo-cluster`를 사용하여 **프론트엔드(Next.js)**와 **백엔드 서비스들**을 함께 배포하는 가이드입니다.

## 📋 현재 클러스터 설정

```cmd
k3d cluster create modorepo-cluster -p "8080:80@loadbalancer" --agents 1
```

- **클러스터 이름**: `modorepo-cluster`
- **포트 매핑**: `8080:80` (호스트:클러스터)
- **에이전트 노드**: 1개

## 🚀 Full-Stack 배포 실행

### 자동 배포 (권장)

```cmd
cd modorepov1
k8s\deploy-fullstack.bat
```

### 수동 배포

```cmd
REM 1. 백엔드 Docker 이미지 빌드
docker build -t lif-app:latest .

REM 2. 프론트엔드 Docker 이미지 빌드
cd frontend
docker build -t lif-frontend:latest .
cd ..

REM 3. 이미지를 k3d 클러스터로 가져오기
k3d image import lif-app:latest -c modorepo-cluster
k3d image import lif-frontend:latest -c modorepo-cluster

REM 4. Kubernetes 리소스 배포
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/postgres-configmap.yaml
kubectl apply -f k8s/postgres-pvc.yaml
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/postgres-service.yaml

REM PostgreSQL 준비 대기
kubectl wait --for=condition=Available deployment/postgres -n lif-system --timeout=300s

REM 5. 백엔드 애플리케이션 배포
kubectl apply -f k8s/app-deployment.yaml
kubectl apply -f k8s/app-service.yaml
kubectl apply -f k8s/app-hpa.yaml

REM 6. 프론트엔드 애플리케이션 배포
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml
kubectl apply -f k8s/frontend-hpa.yaml

REM 7. Ingress 설정
kubectl apply -f k8s/ingress.yaml
```

## 🌐 접속 방법 (포트 분리)

### 🎯 **분리된 포트 접근**
프론트엔드와 백엔드가 별도 포트로 분리되어 NextAuth 문제가 해결되었습니다!

### 🎨 **프론트엔드 (3000 포트)**
```cmd
REM 프론트엔드 메인 페이지
http://localhost:3000

REM NextAuth 구글 로그인 (정상 작동!)
http://localhost:3000/api/auth/signin

REM 기타 프론트엔드 페이지들
http://localhost:3000/dashboard
http://localhost:3000/profile
```

### 🚀 **백엔드 API (8080 포트)**
```cmd
REM 백엔드 API 문서 (Swagger UI)
http://localhost:8080/docs

REM 백엔드 ReDoc
http://localhost:8080/redoc

REM 헬스 체크
http://localhost:8080/health

REM OpenAPI JSON 스키마
http://localhost:8080/openapi.json
```

### 🔧 각 백엔드 서비스 엔드포인트
- **Finance Service**: `http://localhost:8080/finance`
- **Stock Service**: `http://localhost:8080/stock`
- **ESG Service**: `http://localhost:8080/esg`
- **Ratio Service**: `http://localhost:8080/ratio`
- **News Service**: `http://localhost:8080/news`
- **PDF Service**: `http://localhost:8080/pdf`

### 🔍 **MSA 연결 구조**
```
브라우저 → http://localhost:3000 (프론트엔드)
         ↓ API 호출
         → http://localhost:8080 (백엔드 Gateway)
         ↓ 내부 라우팅
         → 각 마이크로서비스들
```

### 🔐 **NextAuth 구글 로그인**
- **로그인 페이지**: `http://localhost:3000/auth/login`
- **NextAuth API**: `http://localhost:3000/api/auth/*`
- **구글 OAuth 콜백**: `http://localhost:3000/api/auth/callback/google`

이제 구글 로그인이 정상적으로 작동합니다! ✅

## 📊 모니터링

### 파드 상태 확인
```cmd
kubectl get pods -n lif-system
kubectl get hpa -n lif-system
```

### 로그 확인
```cmd
REM 프론트엔드 로그
kubectl logs -f deployment/lif-frontend -n lif-system

REM 백엔드 로그
kubectl logs -f deployment/lif-app -n lif-system
```

### 실시간 모니터링 (PowerShell)
```powershell
# PowerShell에서 실행
while ($true) { 
    Clear-Host
    Write-Host "=== 파드 상태 ===" -ForegroundColor Green
    kubectl get pods -n lif-system
    Write-Host "`n=== HPA 상태 ===" -ForegroundColor Yellow
    kubectl get hpa -n lif-system
    Start-Sleep 3
}
```

## 🔧 스케일링 및 로드밸런싱

### 자동 스케일링 (HPA) 설정

#### 프론트엔드 스케일링
- **최소 레플리카**: 1개 (다운스케일링 지원)
- **최대 레플리카**: 8개
- **CPU 임계값**: 60%
- **메모리 임계값**: 70%
- **다운스케일링**: 5분 안정화 후 20%씩 감소

#### 백엔드 스케일링
- **최소 레플리카**: 2개
- **최대 레플리카**: 10개
- **CPU 임계값**: 70%
- **메모리 임계값**: 80%

### 수동 스케일링
```cmd
REM 프론트엔드 파드 수 조정
kubectl scale deployment lif-frontend --replicas=5 -n lif-system

REM 백엔드 파드 수 조정
kubectl scale deployment lif-app --replicas=5 -n lif-system

REM 현재 상태 확인
kubectl get pods -n lif-system
```

### 스케일링 테스트
```cmd
k8s\test-fullstack-scaling.bat
```

## 🧹 정리

```cmd
k8s\cleanup.bat
```

## 🔍 트러블슈팅

### 파드가 시작되지 않는 경우
```cmd
kubectl describe pod <pod-name> -n lif-system
kubectl logs <pod-name> -n lif-system
```

### 이미지 문제
```cmd
REM 이미지 다시 가져오기
k3d image import lif-app:latest -c modorepo-cluster
k3d image import lif-frontend:latest -c modorepo-cluster
```

### 서비스 접속 문제
```cmd
REM 서비스 상태 확인
kubectl get svc -n lif-system

REM Ingress 상태 확인
kubectl get ingress -n lif-system

REM 개별 서비스 직접 접속 테스트 (필요시)
kubectl port-forward -n lif-system svc/lif-frontend 3000:80
kubectl port-forward -n lif-system svc/lif-gateway 8080:80
```

### API 연결 문제
```cmd
REM 프론트엔드에서 백엔드 API 연결 테스트
kubectl exec -it deployment/lif-frontend -n lif-system -- wget -qO- http://lif-gateway/health

REM Ingress를 통한 연결 테스트
curl http://localhost:8080/health
curl http://localhost:8080/docs
```

### Windows 특정 문제

#### Docker Desktop 문제
```cmd
REM Docker Desktop이 실행 중인지 확인
docker version
```

#### PowerShell 실행 정책 문제
```powershell
# PowerShell을 관리자 권한으로 실행 후
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### WSL2 관련 문제
```cmd
REM WSL2가 실행 중인지 확인
wsl --list --verbose
```

## 📈 성능 최적화

### 프론트엔드 리소스 조정
`k8s/frontend-deployment.yaml`에서 리소스 요청/제한 조정:

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "100m"
  limits:
    memory: "512Mi"
    cpu: "250m"
```

### 백엔드 리소스 조정
`k8s/app-deployment.yaml`에서 리소스 요청/제한 조정:

```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "1Gi"
    cpu: "500m"
```

### HPA 임계값 조정

#### 프론트엔드 HPA (`k8s/frontend-hpa.yaml`)
```yaml
metrics:
- type: Resource
  resource:
    name: cpu
    target:
      type: Utilization
      averageUtilization: 60  # 프론트엔드 CPU 임계값
```

#### 백엔드 HPA (`k8s/app-hpa.yaml`)
```yaml
metrics:
- type: Resource
  resource:
    name: cpu
    target:
      type: Utilization
      averageUtilization: 70  # 백엔드 CPU 임계값
```

## 🏗️ 아키텍처

### Full-Stack 구조
```
┌─────────────────┐    ┌─────────────────┐
│   프론트엔드      │    │     백엔드       │
│   (Next.js)     │────│  (단일체 파드)    │
│   1-8 파드      │    │   2-10 파드     │
└─────────────────┘    └─────────────────┘
         │                       │
         └───────────────────────┘
                   │
         ┌─────────────────┐
         │   PostgreSQL    │
         │    (1 파드)     │
         └─────────────────┘
```

### 로드 밸런싱
- **프론트엔드**: Kubernetes Service를 통한 자동 로드 밸런싱
- **백엔드**: 여러 파드 인스턴스 간 트래픽 분산
- **Ingress**: 단일 진입점을 통한 라우팅

### 다운스케일링 특징
- **프론트엔드**: 최소 1개 파드까지 다운스케일 가능
- **백엔드**: 최소 2개 파드 유지 (고가용성)
- **안정화 기간**: 5분 대기 후 점진적 다운스케일

### 스케일 아웃
- **자동 스케일링**: CPU/메모리 사용률 기반
- **빠른 업스케일**: 부하 증가 시 즉시 대응
- **보수적 다운스케일**: 안정성을 위한 점진적 감소

## 💡 Windows 사용 팁

1. **명령 프롬프트(cmd) 사용 권장**: PowerShell보다 cmd에서 더 안정적으로 동작합니다.
2. **Docker Desktop 확인**: Docker Desktop이 실행 중이고 WSL2 백엔드를 사용하는지 확인하세요.
3. **방화벽 설정**: Windows 방화벽에서 포트 8080이 허용되어 있는지 확인하세요.
4. **경로 구분자**: Windows에서는 `\`를 사용합니다 (예: `k8s\deploy-fullstack.bat`).
5. **단일 포트 접근**: 모든 서비스가 8080 포트로 통합되어 관리가 간편합니다.

## 🎯 배포 시나리오

### 개발 환경
```cmd
REM 빠른 개발용 배포 (최소 리소스)
kubectl scale deployment lif-frontend --replicas=1 -n lif-system
kubectl scale deployment lif-app --replicas=2 -n lif-system
```

### 프로덕션 환경
```cmd
REM 고가용성 배포 (충분한 리소스)
kubectl scale deployment lif-frontend --replicas=3 -n lif-system
kubectl scale deployment lif-app --replicas=5 -n lif-system
```

### 부하 테스트 환경
```cmd
REM 최대 성능 테스트
kubectl scale deployment lif-frontend --replicas=8 -n lif-system
kubectl scale deployment lif-app --replicas=10 -n lif-system
```

이제 프론트엔드와 백엔드가 함께 배포되는 완전한 Full-Stack k3d 환경이 구축되었습니다! 🎉

### 주요 특징
- ✅ **로드밸런싱**: 프론트엔드와 백엔드 모두 다중 파드로 부하 분산
- ✅ **다운스케일링**: 프론트엔드는 1개까지, 백엔드는 2개까지 자동 다운스케일
- ✅ **자동 스케일링**: CPU/메모리 기반 HPA로 자동 확장/축소
- ✅ **통합 접속**: 단일 URL(localhost:8080)로 프론트엔드와 API 모두 접근
- ✅ **모니터링**: 실시간 파드 상태 및 스케일링 모니터링 