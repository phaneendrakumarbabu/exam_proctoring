/* ══════════════════════════════════════════════
   ExamGuard — Proctor Monitor
   Handles: fullscreen, tab-switch, frame capture
   ══════════════════════════════════════════════ */

class ProctorMonitor {
  constructor({ studentId, onScore, onEvent, frameInterval = 4000 }) {
    this.studentId     = studentId;
    this.onScore       = onScore || (() => {});
    this.onEvent       = onEvent || (() => {});
    this.frameInterval = frameInterval;

    this._videoEl      = null;
    this._stream       = null;
    this._frameTimer   = null;
    this._active       = false;
    this._fsExits      = 0;
    this._fsWarned     = false;

    this._boundFSChange  = this._onFSChange.bind(this);
    this._boundVisChange = this._onVisChange.bind(this);
    this._boundBlur      = this._onBlur.bind(this);
    this._boundKeydown   = this._onKeydown.bind(this);
    this._boundCtxMenu   = e => e.preventDefault();
  }

  /* ── Start all monitoring ── */
  async start(videoEl) {
    this._videoEl = videoEl;
    this._active  = true;

    // Camera
    try {
      this._stream = await navigator.mediaDevices.getUserMedia({ video: { width:640, height:480 }, audio: false });
      videoEl.srcObject = this._stream;
      await videoEl.play();
    } catch (e) {
      throw new Error('Camera access denied. Webcam is required for this exam.');
    }

    // Attach browser monitors
    document.addEventListener('fullscreenchange',       this._boundFSChange);
    document.addEventListener('webkitfullscreenchange', this._boundFSChange);
    document.addEventListener('visibilitychange',       this._boundVisChange);
    window  .addEventListener('blur',                   this._boundBlur);
    document.addEventListener('contextmenu',            this._boundCtxMenu);
    document.addEventListener('keydown',                this._boundKeydown);

    // Start periodic frame analysis
    this._frameTimer = setInterval(() => this._analyzeFrame(), this.frameInterval);

    // Request fullscreen
    try { await document.documentElement.requestFullscreen(); } catch (_) {}
  }

  /* ── Stop everything ── */
  stop() {
    this._active = false;
    clearInterval(this._frameTimer);

    if (this._stream) this._stream.getTracks().forEach(t => t.stop());

    document.removeEventListener('fullscreenchange',       this._boundFSChange);
    document.removeEventListener('webkitfullscreenchange', this._boundFSChange);
    document.removeEventListener('visibilitychange',       this._boundVisChange);
    window  .removeEventListener('blur',                   this._boundBlur);
    document.removeEventListener('contextmenu',            this._boundCtxMenu);
    document.removeEventListener('keydown',                this._boundKeydown);

    try { document.exitFullscreen(); } catch (_) {}
  }

  /* ── Fullscreen handler ── */
  _onFSChange() {
    const isFS = !!document.fullscreenElement;
    if (!isFS && this._active) {
      this._fsExits++;
      if (this._fsExits === 1) {
        // First exit → warn only
        EG.toast('⚠ Please return to fullscreen immediately!', 'warning', 4000);
        EG.flashBorder(3000);
        this.onEvent('__warning__', 'First fullscreen exit — warning only');
      } else {
        this._reportEvent('fullscreen_exit');
      }
    }
  }

  /* ── Visibility / tab handler ── */
  _onVisChange() {
    if (document.hidden && this._active) {
      this._reportEvent('tab_switch');
    }
  }

  /* ── Window blur (alt-tab, minimise) ── */
  _onBlur() {
    if (this._active) {
      this._reportEvent('tab_switch');
    }
  }

  /* ── Keyboard shortcuts ── */
  _onKeydown(e) {
    const forbidden = ['F12','F11'];
    const ctrlKeys  = ['c','v','x','a','p','s','u','j','i'];
    if (forbidden.includes(e.key)) { e.preventDefault(); return; }
    if ((e.ctrlKey || e.metaKey) && ctrlKeys.includes(e.key.toLowerCase())) {
      e.preventDefault();
    }
    if (e.ctrlKey && e.shiftKey && ['i','j','c'].includes(e.key.toLowerCase())) {
      e.preventDefault();
      this._reportEvent('tab_switch');
    }
  }

  /* ── Capture + send frame ── */
  async _analyzeFrame() {
    if (!this._active || !this._videoEl) return;
    const frame = EG.captureFrame(this._videoEl);
    try {
      const data = await EG.post('/api/analyze-frame', {
        student_id: this.studentId,
        frame,
      });
      if (typeof data.integrity_score === 'number') this.onScore(data.integrity_score);
      if (Array.isArray(data.events)) {
        data.events.forEach(ev => this.onEvent(ev));
      }
      // Also pass analysis data for face detection status
      if (data.analysis) {
        this.onEvent('__analysis__', data.analysis);
      }
      return data;
    } catch (_) {
      // Backend unreachable — keep going
    }
  }

  /* ── Report a browser event to backend ── */
  async _reportEvent(eventType) {
    if (!this._active) return;
    EG.flashBorder();
    EG.toast(this._toastMsg(eventType), 'danger');
    this.onEvent(eventType);
    try {
      const data = await EG.post('/api/report-event', {
        student_id: this.studentId,
        event_type: eventType,
      });
      if (typeof data.integrity_score === 'number') this.onScore(data.integrity_score);
    } catch (_) {
      // Deduct locally as fallback
      const pen = EG.PENALTIES[eventType] || 5;
      // caller handles local score update via onEvent
    }
  }

  _toastMsg(type) {
    const msgs = {
      tab_switch:       '🔄 Tab switch detected! −10 pts',
      fullscreen_exit:  '⛶ Fullscreen exit detected! −10 pts',
      no_face:          '❌ No face detected! −10 pts',
      multiple_faces:   '👥 Multiple faces! −20 pts',
      phone_detected:   '📱 Phone detected! −25 pts',
      looking_away:     '👀 Looking away! −5 pts',
      head_turned:      '↩ Head turned! −5 pts',
    };
    return msgs[type] || `⚠ ${type.replace(/_/g,' ')} detected`;
  }

  /* ── Is currently in fullscreen ── */
  get isFullscreen() { return !!document.fullscreenElement; }
}
