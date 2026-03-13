@echo off
echo.
echo  ExamGuard -- AI Exam Proctoring System
echo ==========================================
echo.

cd /d "%~dp0"

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -q flask flask-cors opencv-python mediapipe numpy Pillow

echo.
echo Initializing database...
python -c "import sys; sys.path.insert(0,'backend'); from event_logger import EventLogger; el=EventLogger('database/exam_logs.db'); el.init_db()"

echo.
echo Starting server...
echo    Open: http://localhost:5000
echo.
cd backend
python app.py
pause
