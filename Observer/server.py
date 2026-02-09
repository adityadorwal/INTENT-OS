#!/usr/bin/env python3
"""
Productivity Tracker - Dashboard Server
Simple HTTP server to view your productivity stats
"""

import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse
from analyzer import ProductivityAnalyzer
from pathlib import Path


class DashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Use main folder database (centralized location)
        current_dir = Path(__file__).parent
        self.analyzer = ProductivityAnalyzer(str(current_dir / "productivity_data.db"))
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
        else:
            # Serve static files
            super().do_GET()
    
    def send_json_response(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())


def start_server(port=8000):
    """Start the dashboard server"""
    server_address = ('127.0.0.1', port)  # Localhost only for security
    httpd = HTTPServer(server_address, DashboardHandler)
    
    print("=" * 60)
    print(f"  PRODUCTIVITY TRACKER - Dashboard Server")
    print("=" * 60)
    print(f"\n🌐 Dashboard running at: http://localhost:{port}")
    print(f"🔒 Server bound to localhost only (secure)")
    print(f"📊 Open dashboard.html in your browser")
    print(f"\n   Available endpoints:")
    print(f"   • http://localhost:{port}/api/daily")
    print(f"   • http://localhost:{port}/api/weekly")
    print(f"   • http://localhost:{port}/api/monthly")
    print(f"   • http://localhost:{port}/api/overall")
    print(f"\n   Press Ctrl+C to stop the server")
    print("=" * 60 + "\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")


if __name__ == "__main__":
    start_server()
