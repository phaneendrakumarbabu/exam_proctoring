"""
ExamGuard — Flask Backend
Main entrypoint for Vercel deployment
"""
import os
import sys

# Add project paths
ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND = os.path.join(ROOT, 'backend')
sys.path.insert(0, BACKEND)
sys.path.insert(0, os.path.join(ROOT, 'ai_modules'))

# Import the Flask app from backend
from backend.app import app as flask_app

# Export app for Vercel
app = flask_app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

