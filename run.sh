#!/bin/bash
# ══════════════════════════════════════════════════════
#  ExamGuard — AI Proctoring System Setup & Launch
# ══════════════════════════════════════════════════════

set -e
cd "$(dirname "$0")"

echo ""
echo "🛡️  ExamGuard — AI Exam Proctoring System"
echo "══════════════════════════════════════════"
echo ""

# Create virtual environment if needed
if [ ! -d "venv" ]; then
  echo "📦 Creating Python virtual environment..."
  python3 -m venv venv
fi

source venv/bin/activate

echo "📥 Installing dependencies..."
pip install -q flask flask-cors opencv-python mediapipe numpy Pillow

echo ""
echo "🗄️  Initializing database..."
python3 -c "
import sys, os
sys.path.insert(0, 'backend')
from event_logger import EventLogger
el = EventLogger('database/exam_logs.db')
el.init_db()
"

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Starting Flask server..."
echo "   → Login:     http://localhost:5000"
echo "   → Exam:      http://localhost:5000/exam"
echo "   → Dashboard: http://localhost:5000/dashboard"
echo ""
echo "Demo credentials:"
echo "   STU001 / pass123"
echo "   STU002 / pass123"
echo "   ADMIN  / admin123"
echo ""

cd backend
python3 app.py
