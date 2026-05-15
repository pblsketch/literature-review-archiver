@echo off
chcp 65001 >nul
echo ========================================================
echo  논문 분석 AI (Literature Review Archiver) 실행 도우미
echo ========================================================
echo.

:: 1. 파이썬 확인
echo [1/4] 파이썬(Python) 설치 여부를 확인합니다...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [오류] 파이썬이 설치되어 있지 않습니다.
    echo.
    echo 1. https://www.python.org/downloads/ 에 접속하세요.
    echo 2. "Download Python" 버튼을 눌러 설치 프로그램을 받으세요.
    echo 3. 설치 시작 화면에서 **"Add Python to PATH"** 체크박스를 꼭! 체크하고 Install Now를 누르세요.
    echo.
    echo 설치 후 이 파일을 다시 실행해주세요.
    pause
    exit
)
echo [확인완료] 파이썬이 설치되어 있습니다.
echo.

:: 2. 가상환경 설정 (선택사항이지만 권장, 여기서는 단순화를 위해 생략하거나 간단히 처리)
:: 초보자를 위해 복잡한 venv 처리보다는 바로 설치 시도 (또는 venv 자동 생성)
:: venv가 안전하므로 venv 생성 시도
if not exist "venv" (
    echo [2/4] 가상환경(venv)을 생성합니다...
    python -m venv venv
)
call venv\Scripts\activate

:: 3. 패키지 설치
echo [3/4] 필요한 프로그램(라이브러리)을 설치/업데이트합니다. (몇 분 걸릴 수 있습니다)
pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo [오류] 설치 중 문제가 발생했습니다.
    echo 인터넷 연결을 확인하거나, 관리자 권한으로 실행해보세요.
    pause
    exit
)
echo [설치완료] 준비가 끝났습니다.
echo.

:: 4. 스트림릿 실행
echo [4/4] 프로그램을 실행합니다!
echo 잠시 후 인터넷 브라우저가 자동으로 열립니다.
echo 실행을 종료하려면 이 검은 창을 닫으세요.
echo.
streamlit run app.py

pause
