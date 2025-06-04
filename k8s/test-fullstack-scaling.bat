@echo off
echo ========================================
echo 🧪 Full-Stack 스케일링 테스트
echo ========================================

REM 현재 상태 확인
echo.
echo 📊 현재 파드 상태:
kubectl get pods -n lif-system -l app=lif-frontend
kubectl get pods -n lif-system -l app=lif-app
echo.
echo 📈 현재 HPA 상태:
kubectl get hpa -n lif-system

echo.
echo ========================================
echo 🔥 부하 테스트 시작
echo ========================================

REM 프론트엔드 부하 테스트
echo.
echo 🎨 프론트엔드 부하 테스트 (30초)...
start /B powershell -Command "for ($i=1; $i -le 100; $i++) { try { Invoke-WebRequest -Uri 'http://localhost:30090' -UseBasicParsing | Out-Null; Write-Host \"Frontend Request $i completed\" } catch { Write-Host \"Frontend Request $i failed\" } }"

REM 백엔드 부하 테스트
echo.
echo 🚀 백엔드 부하 테스트 (30초)...
start /B powershell -Command "for ($i=1; $i -le 100; $i++) { try { Invoke-WebRequest -Uri 'http://localhost:30080/health' -UseBasicParsing | Out-Null; Write-Host \"Backend Request $i completed\" } catch { Write-Host \"Backend Request $i failed\" } }"

REM 스케일링 모니터링
echo.
echo 📊 스케일링 모니터링 (60초간)...
for /L %%i in (1,1,12) do (
    echo.
    echo === 모니터링 %%i/12 ===
    echo 시간: %TIME%
    echo.
    echo 프론트엔드 파드:
    kubectl get pods -n lif-system -l app=lif-frontend --no-headers | find /c /v ""
    echo.
    echo 백엔드 파드:
    kubectl get pods -n lif-system -l app=lif-app --no-headers | find /c /v ""
    echo.
    echo HPA 상태:
    kubectl get hpa -n lif-system --no-headers
    echo.
    timeout /t 5 /nobreak >nul
)

echo.
echo ========================================
echo 📉 다운스케일링 테스트
echo ========================================

echo.
echo ⏳ 부하 중단 후 다운스케일링 대기 (5분)...
echo 다운스케일링은 안정화 기간(5분) 후에 시작됩니다.

for /L %%i in (1,1,30) do (
    echo.
    echo === 다운스케일링 모니터링 %%i/30 ===
    echo 시간: %TIME%
    echo.
    echo 프론트엔드 파드 수:
    kubectl get pods -n lif-system -l app=lif-frontend --no-headers | find /c /v ""
    echo.
    echo 백엔드 파드 수:
    kubectl get pods -n lif-system -l app=lif-app --no-headers | find /c /v ""
    echo.
    echo HPA 상태:
    kubectl get hpa -n lif-system
    echo.
    timeout /t 10 /nobreak >nul
)

echo.
echo ========================================
echo ✅ 스케일링 테스트 완료
echo ========================================

echo.
echo 📊 최종 상태:
kubectl get pods -n lif-system
echo.
kubectl get hpa -n lif-system

echo.
echo 💡 수동 스케일링 명령어:
echo   kubectl scale deployment lif-frontend --replicas=5 -n lif-system
echo   kubectl scale deployment lif-app --replicas=5 -n lif-system
echo.
pause 