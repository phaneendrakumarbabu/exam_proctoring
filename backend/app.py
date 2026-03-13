"""
ExamGuard — Flask Backend
Run from project root: python backend/app.py
"""
import os, sys, base64, json
from datetime import datetime

# Add project paths
ROOT    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BACKEND)
sys.path.insert(0, os.path.join(ROOT, 'ai_modules'))

from flask import Flask, request, jsonify, session, send_from_directory, redirect

try:
    from flask_cors import CORS
    _has_cors = True
except ImportError:
    _has_cors = False

from integrity_engine import IntegrityEngine
from event_logger      import EventLogger

# ── App setup ──────────────────────────────────────────────────────────────
app = Flask(
    __name__,
    static_folder=os.path.join(ROOT, 'static'),
    template_folder=os.path.join(ROOT, 'frontend'),
)
app.secret_key = 'examguard_secret_key_2024_change_in_prod'

if _has_cors:
    CORS(app, supports_credentials=True, origins=['*'], allow_headers=['*'], methods=['*'])
else:
    @app.after_request
    def add_cors(resp):
        resp.headers['Access-Control-Allow-Origin']      = '*'
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        resp.headers['Access-Control-Allow-Headers']     = 'Content-Type'
        resp.headers['Access-Control-Allow-Methods']     = 'GET,POST,OPTIONS,PUT,DELETE'
        return resp

DB_PATH = os.path.join(ROOT, 'database', 'exam_logs.db')

engine  = IntegrityEngine()
logger  = EventLogger(DB_PATH)

# In-memory session store  {student_id: {...}}
SESSIONS: dict = {}

# ── Try to import camera analyzer ──────────────────────────────────────────
try:
    from camera_analyzer import CameraAnalyzer
    analyzer = CameraAnalyzer()
    print("[OK] CameraAnalyzer loaded (OpenCV + MediaPipe)")
except Exception as e:
    analyzer = None
    print(f"[WARN] CameraAnalyzer unavailable ({e}). AI analysis disabled.")

# ── Static / HTML routes ───────────────────────────────────────────────────

FRONTEND = os.path.join(ROOT, 'frontend')
STATIC   = os.path.join(ROOT, 'static')

@app.route('/')
def index():
    return send_from_directory(FRONTEND, 'login.html')

@app.route('/exam')
def exam_page():
    return send_from_directory(FRONTEND, 'exam.html')

@app.route('/dashboard')
def dashboard_page():
    return send_from_directory(FRONTEND, 'dashboard.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(STATIC, filename)

@app.route('/favicon.ico')
def favicon():
    return '', 204

# ── Handle preflight OPTIONS ───────────────────────────────────────────────
@app.route('/api/<path:path>', methods=['OPTIONS'])
def options_handler(path):
    return '', 204

# ── Auth ───────────────────────────────────────────────────────────────────

@app.route('/api/login', methods=['POST'])
def api_login():
    data       = request.get_json(force=True) or {}
    student_id = data.get('student_id','').strip()
    password   = data.get('password','').strip()

    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        'SELECT * FROM students WHERE student_id=? AND password=?',
        (student_id, password)
    ).fetchone()
    conn.close()

    if row:
        session['student_id'] = student_id
        SESSIONS[student_id] = {
            'integrity_score': 100,
            'exam_start':      datetime.now().isoformat(),
            'events':          [],
            'active':          True,
        }
        return jsonify({'success': True, 'student_id': student_id, 'name': row['name']})
    return jsonify({'success': False, 'message': 'Invalid credentials. Please try again.'}), 401


@app.route('/api/logout', methods=['POST'])
def api_logout():
    data = request.get_json(force=True) or {}
    sid  = data.get('student_id')
    if sid in SESSIONS:
        SESSIONS[sid]['active'] = False
    session.clear()
    return jsonify({'success': True})

# ── Frame analysis ─────────────────────────────────────────────────────────

@app.route('/api/analyze-frame', methods=['POST'])
def api_analyze_frame():
    data       = request.get_json(force=True) or {}
    student_id = data.get('student_id','').strip()
    frame_b64  = data.get('frame','')

    if not student_id:
        return jsonify({'error': 'Missing student_id'}), 400

    _ensure_session(student_id)

    # Decode frame bytes
    events_detected = []
    analysis        = {'faces':1, 'events':[], 'looking_away':False}

    if analyzer and frame_b64:
        try:
            raw = frame_b64.split(',',1)[-1]  # strip data:... prefix
            frame_bytes = base64.b64decode(raw)
            analysis    = analyzer.analyze(frame_bytes)
            events_detected = analysis.get('events', [])
        except Exception as ex:
            print(f"Frame analysis error: {ex}")

    # Apply penalties
    for ev in events_detected:
        _apply_event(student_id, ev)

    return jsonify({
        'integrity_score': SESSIONS[student_id]['integrity_score'],
        'events':          events_detected,
        'analysis':        analysis,
    })

# ── Browser event report ───────────────────────────────────────────────────

@app.route('/api/report-event', methods=['POST'])
def api_report_event():
    data       = request.get_json(force=True) or {}
    student_id = data.get('student_id','').strip()
    event_type = data.get('event_type','').strip()

    if not student_id or not event_type:
        return jsonify({'error': 'Missing fields'}), 400

    _ensure_session(student_id)
    deduction = _apply_event(student_id, event_type)

    return jsonify({
        'integrity_score': SESSIONS[student_id]['integrity_score'],
        'deduction':       deduction,
        'event':           event_type,
    })

# ── Status / admin ─────────────────────────────────────────────────────────

@app.route('/api/status/<student_id>')
def api_status(student_id):
    if student_id in SESSIONS:
        return jsonify(SESSIONS[student_id])
    return jsonify({'error': 'Not found'}), 404


@app.route('/api/all-students')
def api_all_students():
    return jsonify(list(SESSIONS.items()))


@app.route('/api/logs/<student_id>')
def api_logs(student_id):
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        'SELECT * FROM exam_events WHERE student_id=? ORDER BY timestamp DESC LIMIT 200',
        (student_id,)
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/report/<student_id>')
def api_report(student_id):
    if student_id not in SESSIONS:
        return jsonify({'error': 'Session not found'}), 404

    sess  = SESSIONS[student_id]
    score = sess['integrity_score']
    evs   = sess['events']
    ti    = engine.get_trust_level(score)

    return jsonify({
        'student_id':      student_id,
        'integrity_score': score,
        'trust_level':     ti['level'],
        'grade':           ti['grade'],
        'total_events':    len(evs),
        'events':          evs[-50:],
        'exam_start':      sess.get('exam_start'),
    })


@app.route('/api/ping')
def api_ping():
    return jsonify({'status': 'ok', 'time': datetime.now().isoformat(), 'message': 'Server is reachable'})

@app.route('/test')
def test():
    return jsonify({'test': 'ok', 'api_base': 'http://localhost:5000'})

# ── Helpers ────────────────────────────────────────────────────────────────

def _ensure_session(student_id: str):
    if student_id not in SESSIONS:
        SESSIONS[student_id] = {
            'integrity_score': 100,
            'exam_start':      datetime.now().isoformat(),
            'events':          [],
            'active':          True,
        }


def _apply_event(student_id: str, event_type: str) -> int:
    deduction = engine.get_penalty(event_type)
    current   = SESSIONS[student_id]['integrity_score']
    new_score = max(0, current - deduction)
    SESSIONS[student_id]['integrity_score'] = new_score
    SESSIONS[student_id]['events'].append({
        'type':      event_type,
        'time':      datetime.now().isoformat(),
        'deduction': deduction,
    })
    logger.log(student_id, event_type, deduction)
    return deduction

# ── Entry point ────────────────────────────────────────────────────────────

if __name__ == '__main__':
    os.makedirs(os.path.join(ROOT, 'database'), exist_ok=True)
    logger.init_db()
    print()
    print("  [SHIELD] ExamGuard - AI Exam Proctoring System")
    print("  =============================================")
    print("  Login Page  ->  http://localhost:8000")
    print("  Exam Page   ->  http://localhost:8000/exam")
    print("  Dashboard   ->  http://localhost:8000/dashboard")
    print()
    print("  Demo credentials:")
    print("    STU001 / pass123  .  STU002 / pass123")
    print("    STU003 / pass123  .  ADMIN  / admin123")
    print()
    app.run(host='0.0.0.0', port=8000, debug=True, use_reloader=False)
