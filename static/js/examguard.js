/* ══════════════════════════════════════════════
   ExamGuard — Shared JS Utilities
   ══════════════════════════════════════════════ */

const EG = (() => {

  /* ── Config ── */
  const API_BASE = window.location.origin;

  /* ── Penalty table (mirrors backend) ── */
  const PENALTIES = {
    multiple_faces:    20,
    no_face:           10,
    phone_detected:    25,
    book_detected:     10,
    looking_away:       5,
    tab_switch:        10,
    fullscreen_exit:   10,
    head_turned:        5,
    suspicious_object: 15,
    rapid_movement:     5,
    copy_paste_attempt: 15,
    keyboard_shortcut_attempt: 15,
  };

  const EVENT_META = {
    tab_switch:        { icon:'🔄', label:'Tab switch detected' },
    fullscreen_exit:   { icon:'⛶',  label:'Fullscreen exit' },
    no_face:           { icon:'❌', label:'No face in frame' },
    multiple_faces:    { icon:'👥', label:'Multiple faces detected' },
    phone_detected:    { icon:'📱', label:'Phone detected' },
    book_detected:     { icon:'📚', label:'Book / notes detected' },
    looking_away:      { icon:'👀', label:'Looking away from screen' },
    head_turned:       { icon:'↩',  label:'Head turned away' },
    suspicious_object: { icon:'📦', label:'Suspicious object' },
    rapid_movement:    { icon:'⚡', label:'Rapid movement' },
    copy_paste_attempt:{ icon:'📋', label:'Copy/Paste attempt' },
    keyboard_shortcut_attempt:{ icon:'⌨', label:'Keyboard shortcut attempt' },
  };

  /* ── Trust levels ── */
  function trustInfo(score) {
    if (score >= 90) return { level:'Excellent', cls:'score-excellent', pillCls:'pill-success',  grade:'A' };
    if (score >= 75) return { level:'Good',      cls:'score-good',      pillCls:'pill-success',  grade:'B' };
    if (score >= 60) return { level:'Medium',    cls:'score-medium',    pillCls:'pill-warning',  grade:'C' };
    if (score >= 40) return { level:'Low',       cls:'score-low',       pillCls:'pill-warning',  grade:'D' };
    return               { level:'Critical',   cls:'score-critical',  pillCls:'pill-danger',   grade:'F' };
  }

  /* ── API helpers ── */
  async function api(path, opts = {}) {
    try {
      const url = API_BASE + path;
      console.log('API call to:', url);
      const res = await fetch(url, {
        credentials: 'include',
        headers: { 'Content-Type': 'application/json', ...opts.headers },
        ...opts,
        body: opts.body ? JSON.stringify(opts.body) : undefined,
      });
      console.log('Response status:', res.status);
      
      // Try to parse JSON response
      let data;
      try {
        data = await res.json();
      } catch {
        data = { error: 'Invalid JSON response' };
      }
      
      // Return data regardless of status (let caller handle it)
      return data;
    } catch (e) {
      console.error('Fetch error:', e);
      throw e;
    }
  }

  const get  = path => api(path);
  const post = (path, body) => api(path, { method: 'POST', body });

  /* ── Session storage helpers ── */
  const session = {
    get studentId()   { return localStorage.getItem('student_id')   || ''; },
    get studentName() { return localStorage.getItem('student_name') || 'Student'; },
    set(id, name)     { localStorage.setItem('student_id', id); localStorage.setItem('student_name', name); },
    clear()           { localStorage.clear(); },
    valid()           { return !!this.studentId; },
  };

  /* ── Toast notification ── */
  let _toastTimer;
  function toast(msg, type = 'danger', duration = 3000) {
    let el = document.getElementById('eg-toast');
    if (!el) {
      el = document.createElement('div');
      el.id = 'eg-toast';
      el.style.cssText = `
        position:fixed; top:80px; left:50%; transform:translateX(-50%) translateY(-16px);
        padding:.7rem 1.4rem; border-radius:12px; font-family:'Space Mono',monospace;
        font-size:.82rem; font-weight:700; z-index:9999; pointer-events:none;
        transition:opacity .25s,transform .25s; opacity:0; white-space:nowrap;
        box-shadow:0 4px 24px rgba(0,0,0,.4);
      `;
      document.body.appendChild(el);
    }
    const colours = {
      danger:  { bg:'rgba(255,56,96,.95)',  text:'#fff' },
      warning: { bg:'rgba(255,170,0,.92)',  text:'#000' },
      success: { bg:'rgba(0,255,136,.92)',  text:'#000' },
      info:    { bg:'rgba(0,212,255,.92)',  text:'#000' },
    };
    const c = colours[type] || colours.info;
    el.style.background = c.bg;
    el.style.color = c.text;
    el.textContent = msg;
    // Show
    requestAnimationFrame(() => {
      el.style.opacity = '1';
      el.style.transform = 'translateX(-50%) translateY(0)';
    });
    clearTimeout(_toastTimer);
    _toastTimer = setTimeout(() => {
      el.style.opacity = '0';
      el.style.transform = 'translateX(-50%) translateY(-16px)';
    }, duration);
  }

  /* ── Flash the red border warning ── */
  function flashBorder(duration = 2500) {
    let el = document.getElementById('eg-border-flash');
    if (!el) {
      el = document.createElement('div');
      el.id = 'eg-border-flash';
      el.style.cssText = `
        position:fixed;inset:0;pointer-events:none;z-index:9998;
        border:4px solid transparent;border-radius:0;
        transition:border-color .2s;
      `;
      document.body.appendChild(el);
    }
    el.style.borderColor = '#ff3860';
    clearTimeout(el._timer);
    el._timer = setTimeout(() => { el.style.borderColor = 'transparent'; }, duration);
  }

  /* ── Format seconds → MM:SS or HH:MM:SS ── */
  function fmtTime(secs, forceHours = false) {
    const h = Math.floor(secs / 3600);
    const m = Math.floor((secs % 3600) / 60);
    const s = secs % 60;
    const pad = n => String(n).padStart(2, '0');
    return (h > 0 || forceHours)
      ? `${pad(h)}:${pad(m)}:${pad(s)}`
      : `${pad(m)}:${pad(s)}`;
  }

  /* ── Elapsed time string ── */
  function elapsed(startIso) {
    if (!startIso) return '—';
    const secs = Math.round((Date.now() - new Date(startIso).getTime()) / 1000);
    return fmtTime(secs, true);
  }

  /* ── Capture video frame as base64 JPEG ── */
  function captureFrame(videoEl, quality = 0.65) {
    const canvas = document.createElement('canvas');
    canvas.width  = videoEl.videoWidth  || 320;
    canvas.height = videoEl.videoHeight || 240;
    canvas.getContext('2d').drawImage(videoEl, 0, 0);
    return canvas.toDataURL('image/jpeg', quality);
  }

  /* ── Debounce ── */
  function debounce(fn, ms) {
    let t;
    return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
  }

  /* ── Public API ── */
  return {
    API_BASE, PENALTIES, EVENT_META,
    trustInfo, toast, flashBorder, fmtTime, elapsed, captureFrame, debounce,
    session, get, post,
  };
})();
