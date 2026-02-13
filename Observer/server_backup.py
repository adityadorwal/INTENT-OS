#!/usr/bin/env python3
"""
Productivity Tracker - Dashboard Server (FIXED)
Simple HTTP server to view your productivity stats
"""

import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse
from pathlib import Path
import sys
import os

# Add Observer directory to path so we can import analyzer
observer_dir = Path(__file__).parent / "Observer"
sys.path.insert(0, str(observer_dir))

from analyzer import ProductivityAnalyzer


def safe_print(*args, **kwargs):
    """Print safely to consoles that may not support some Unicode characters."""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        try:
            sep = kwargs.get('sep', ' ')
            end = kwargs.get('end', '\n')
            msg = sep.join(str(a) for a in args) + end
            encoding = getattr(sys.stdout, 'encoding', None) or 'utf-8'
            sys.stdout.buffer.write(msg.encode(encoding, errors='replace'))
        except Exception:
            try:
                ascii_msg = sep.join(str(a) for a in args).encode('ascii', 'replace').decode('ascii') + end
                sys.stdout.write(ascii_msg)
            except Exception:
                pass


class DashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # FIXED: Use Observer folder database (correct location)
        observer_dir = Path(__file__).parent / "Observer"
        db_path = observer_dir / "productivity_data.db"
        
        # Verify database exists
        if not db_path.exists():
            safe_print(f"\n[WARNING] Database not found at: {db_path}")
            safe_print("[INFO] Run: python Observer/setup_database.py")
        else:
            safe_print(f"\n[INFO] Using database: {db_path}")
            # Quick check - count records
            import sqlite3
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM window_activity WHERE DATE(timestamp) = DATE('now')")
                today_count = cursor.fetchone()[0]
                safe_print(f"[INFO] Today's records in database: {today_count}")
                conn.close()
            except Exception as e:
                safe_print(f"[WARNING] Could not read database: {e}")
        
        self.analyzer = ProductivityAnalyzer(str(db_path))
        
        # Serve files from current directory (where dashboard.html is)
        current_dir = Path(__file__).parent
        super().__init__(*args, directory=str(current_dir), **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urllib.parse.urlparse(self.path)
        
        # API endpoints
        if parsed_path.path == '/api/daily':
            self.send_json_response(self.analyzer.get_daily_stats())
        elif parsed_path.path == '/api/weekly':
            self.send_json_response(self.analyzer.get_weekly_stats())
        elif parsed_path.path == '/api/monthly':
            self.send_json_response(self.analyzer.get_monthly_stats())
        elif parsed_path.path == '/api/overall':
            self.send_json_response(self.analyzer.get_overall_stats())
        elif parsed_path.path == '/api/test':
            # Test endpoint to verify database
            import sqlite3
            observer_dir = Path(__file__).parent / "Observer"
            db_path = observer_dir / "productivity_data.db"
            
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM window_activity")
                total = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM window_activity WHERE DATE(timestamp) = DATE('now')")
                today = cursor.fetchone()[0]
                conn.close()
                
                self.send_json_response({
                    'status': 'ok',
                    'database': str(db_path),
                    'total_records': total,
                    'today_records': today
                })
            except Exception as e:
                self.send_json_response({
                    'status': 'error',
                    'error': str(e)
                })
        else:
            # Serve static files
            super().do_GET()
    
    def send_json_response(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def log_message(self, format, *args):
        """Override to use safe_print for log messages"""
        safe_print(f"[{self.log_date_time_string()}] {format % args}")


def start_server(port=8000):
    """Start the dashboard server"""
    server_address = ('127.0.0.1', port)  # Localhost only for security
    httpd = HTTPServer(server_address, DashboardHandler)
    
    safe_print("=" * 60)
    safe_print("  PRODUCTIVITY TRACKER - Dashboard Server (FIXED)")
    safe_print("=" * 60)
    safe_print(f"\nDashboard running at: http://localhost:{port}")
    safe_print("Server bound to localhost only (secure)")
    safe_print(f"Open http://localhost:{port}/dashboard.html in your browser")
    safe_print("\n   Available endpoints:")
    safe_print(f"   - http://localhost:{port}/api/daily")
    safe_print(f"   - http://localhost:{port}/api/weekly")
    safe_print(f"   - http://localhost:{port}/api/monthly")
    safe_print(f"   - http://localhost:{port}/api/overall")
    safe_print(f"   - http://localhost:{port}/api/test (diagnostic)")
    safe_print("\n   Press Ctrl+C to stop the server")
    safe_print("=" * 60 + "\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        safe_print("\nServer stopped")


if __name__ == "__main__":
    start_server()