"""
WSGI entry point for Vercel deployment.
"""

import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set the database path for Vercel's ephemeral filesystem
os.environ['DATABASE_PATH'] = '/tmp/metro.db'

from app import app

# Vercel requires the app to be callable as 'app'
application = app
