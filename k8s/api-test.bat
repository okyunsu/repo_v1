@echo off
echo ========================================
echo 🔍 FastAPI 연결 테스트
echo ========================================

echo.
echo 📊 현재 배포 상태 확인...
kubectl get pods -n lif-system
echo.
kubectl get svc -n lif-system

echo.
echo ========================================
echo 🌐 FastAPI Docs 접속 테스트
echo ========================================

echo.
echo 🔗 다음 URL들을 브라우저에서 확인하세요:
echo.
echo === 백엔드 Gateway (8080 포트) ===
echo   📖 Swagger UI:    http://localhost:8080/docs
echo   📚 ReDoc:         http://localhost:8080/redoc  
echo   📄 OpenAPI JSON:  http://localhost:8080/openapi.json
echo   🔍 헬스 체크:     http://localhost:8080/health
echo.
echo === 프론트엔드 (30090 포트) ===
echo   🎨 프론트엔드:    http://localhost:30090

echo.
echo ========================================
echo 🧪 API 엔드포인트 테스트
echo ========================================

echo.
echo 🔍 백엔드 헬스 체크 테스트...
curl -s http://localhost:8080/health
if %ERRORLEVEL% equ 0 (
    echo ✅ 백엔드 Gateway 연결 성공
) else (
    echo ❌ 백엔드 Gateway 연결 실패
)

echo.
echo 🔍 프론트엔드 연결 테스트...
curl -s -o nul -w "HTTP Status: %%{http_code}" http://localhost:30090/
if %ERRORLEVEL% equ 0 (
    echo ✅ 프론트엔드 연결 성공
) else (
    echo ❌ 프론트엔드 연결 실패
)

echo.
echo ========================================
echo 📋 개별 서비스 포트 포워딩 명령어
echo ========================================

echo.
echo 개별 서비스에 직접 접근하려면 다음 명령어를 사용하세요:
echo.
echo   kubectl port-forward -n lif-system svc/lif-finance 8000:8000
echo   # 그 후 http://localhost:8000/docs 접속
echo.
echo   kubectl port-forward -n lif-system svc/lif-stock 8001:8001
echo   # 그 후 http://localhost:8001/docs 접속
echo.
echo   kubectl port-forward -n lif-system svc/lif-esg 8002:8002
echo   # 그 후 http://localhost:8002/docs 접속
echo.
echo   kubectl port-forward -n lif-system svc/lif-ratio 8003:8003
echo   # 그 후 http://localhost:8003/docs 접속
echo.
echo   kubectl port-forward -n lif-system svc/lif-news 8004:8004
echo   # 그 후 http://localhost:8004/docs 접속
echo.
echo   kubectl port-forward -n lif-system svc/lif-pdf 8005:8005
echo   # 그 후 http://localhost:8005/docs 접속

echo.
echo ========================================
echo 💡 FastAPI Docs 사용 팁
echo ========================================

echo.
echo 1. 📖 Swagger UI (http://localhost:8080/docs)
echo    - 인터랙티브한 API 테스트 가능
echo    - "Try it out" 버튼으로 실제 API 호출
echo    - 요청/응답 예시 확인
echo.
echo 2. 📚 ReDoc (http://localhost:8080/redoc)
echo    - 더 깔끔하고 읽기 쉬운 문서
echo    - API 스키마 상세 정보
echo    - 코드 예시 제공
echo.
echo 3. 📄 OpenAPI JSON (http://localhost:8080/openapi.json)
echo    - API 스키마 원본 데이터
echo    - 다른 도구와 연동 시 사용

echo.
echo ========================================
echo ✅ 테스트 완료
echo ========================================
echo.
echo 🎯 요약:
echo   - 백엔드 Gateway: http://localhost:8080
echo   - 백엔드 Docs: http://localhost:8080/docs
echo   - 프론트엔드: http://localhost:30090
echo.
pause 