class IntegrityEngine:
    PENALTIES = {
        'multiple_faces':      20,
        'no_face':             10,
        'phone_detected':      25,
        'book_detected':       10,
        'looking_away':         5,
        'tab_switch':          10,
        'fullscreen_exit':     10,
        'head_turned':          5,
        'suspicious_object':   15,
        'rapid_movement':       5,
    }

    PENALTY_LABELS = {
        'multiple_faces':   '👥 Multiple faces detected',
        'no_face':          '❌ No face in frame',
        'phone_detected':   '📱 Phone detected',
        'book_detected':    '📚 Book detected',
        'looking_away':     '👀 Looking away',
        'tab_switch':       '🔄 Tab switch',
        'fullscreen_exit':  '⛶ Fullscreen exit',
        'head_turned':      '↩ Head turned',
        'suspicious_object':'📦 Suspicious object',
        'rapid_movement':   '⚡ Rapid movement',
    }

    def get_penalty(self, event_type: str) -> int:
        return self.PENALTIES.get(event_type, 5)

    def get_label(self, event_type: str) -> str:
        return self.PENALTY_LABELS.get(event_type, event_type.replace('_', ' ').title())

    def get_trust_level(self, score: int) -> dict:
        if score >= 90:
            return {'level': 'Excellent', 'color': '#00ff88', 'grade': 'A'}
        elif score >= 75:
            return {'level': 'Good', 'color': '#88ff00', 'grade': 'B'}
        elif score >= 60:
            return {'level': 'Medium', 'color': '#ffaa00', 'grade': 'C'}
        elif score >= 40:
            return {'level': 'Low', 'color': '#ff6600', 'grade': 'D'}
        else:
            return {'level': 'Critical', 'color': '#ff0044', 'grade': 'F'}
