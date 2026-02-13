#!/usr/bin/env python3
"""
Productivity Tracker - Dashboard Server
Simple HTTP server to view your productivity stats
"""

import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse
from pathlib import Path
import sys
from analyzer import ProductivityAnalyzer


class DashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        current_dir = Path(__file__).parent
        db_path = current_dir / "productivity_data.db"
        
        print(f"[SERVER] Using database: {db_path}")
        
        # Verify database exists
        if not db_path.exists():
            print(f"[ERROR] Database not found at: {db_path}")
            print("[ERROR] Run: python setup_database.py")
        else:
            # Quick diagnostic
            import sqlite3
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM window_activity WHERE DATE(timestamp) = DATE('now')")
                today_count = cursor.fetchone()[0]
                print(f"[SERVER] Today's records in database: {today_count}")
                conn.close()
            except Exception as e:
                print(f"[ERROR] Database error: {e}")
        
        self.analyzer = ProductivityAnalyzer(str(db_path))
        
        # Serve files from Observer directory (where dashboard.html is)
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
        elif parsed_path.path == '/api/debug':
            # Debug endpoint
            import sqlite3
            current_dir = Path(__file__).parent
            db_path = current_dir / "productivity_data.db"
            
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM window_activity")
                total = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM window_activity WHERE DATE(timestamp) = DATE('now')")
                today = cursor.fetchone()[0]
                
                # Get last 5 entries
                cursor.execute("""
                    SELECT timestamp, app_name, window_title, duration_seconds 
                    FROM window_activity 
                    ORDER BY timestamp DESC 
                    LIMIT 5
                """)
                recent = [{"time": r[0], "app": r[1], "title": r[2], "duration": r[3]} for r in cursor.fetchall()]
                
                conn.close()
                
                self.send_json_response({
                    'database': str(db_path),
                    'total_records': total,
                    'today_records': today,
                    'recent_entries': recent
                })
            except Exception as e:
                self.send_json_response({
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


def start_server(port=8000):
    """Start the dashboard server"""
    server_address = ('127.0.0.1', port)
    httpd = HTTPServer(server_address, DashboardHandler)
    
    print("=" * 60)
    print("  PRODUCTIVITY TRACKER - Dashboard Server")
    print("=" * 60)
    print(f"\nDashboard running at: http://localhost:{port}")
    print(f"Open: http://localhost:{port}/dashboard.html")
    print(f"\nDebug endpoint: http://localhost:{port}/api/debug")
    print("\nPress Ctrl+C to stop")
    print("=" * 60 + "\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")


if __name__ == "__main__":
    start_server()
