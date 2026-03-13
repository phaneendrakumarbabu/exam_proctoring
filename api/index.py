"""
ExamGuard — Flask Backend
Vercel Serverless Function Entry Point
"""
import os
import sys

# Add project paths
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND = os.path.join(ROOT, 'backend')
sys.path.insert(0, BACKEND)
sys.path.insert(0, os.path.join(ROOT, 'ai_modules'))

# Import the Flask app from backend
from backend.app import app

# Export app for Vercel
