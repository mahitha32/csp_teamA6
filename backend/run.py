"""
run.py — Flask entry point
Village Complaint Redressal System - Vemavaram Village

Usage:
  python run.py                    # Development
  gunicorn -w 4 run:app            # Production
"""

import os
from app import create_app

app = create_app(os.getenv("FLASK_ENV", "development"))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print("=" * 55)
    print("  Vemavaram Village CSP — Backend API Server")
    print(f"  Running at: http://127.0.0.1:{port}")
    print(f"  Health:     http://127.0.0.1:{port}/api/health")
    print("=" * 55)
    app.run(host="0.0.0.0", port=port, debug=app.config.get("DEBUG", True))
