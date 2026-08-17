"""Vercel entry point for the Sathya Agencies Flask application."""

import os
import sys

# Make the repository root importable when Vercel executes api/index.py.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import app  # noqa: E402,F401
