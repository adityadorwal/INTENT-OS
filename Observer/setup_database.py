#!/usr/bin/env python3
"""
Database Setup Script
Creates the necessary database tables for the Observer system
"""

import sqlite3
import json
from pathlib import Path

def setup_database():
    """Initialize the productivity tracking database"""
    # Ensure database is created in Observer folder
    current_dir = Path(__file__).parent
    db_path = current_dir / "productivity_data.db"
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create window_activity table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS window_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            window_title TEXT,
            app_name TEXT,
            app_path TEXT,
            duration_seconds REAL,
            category TEXT,
            is_productive BOOLEAN
        )
    """)
    
    # Create indexes for better performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON window_activity(timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_app_name ON window_activity(app_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON window_activity(category)")
    
    conn.commit()
    conn.close()
    
    # Set restrictive file permissions (owner only)
    try:
        import stat
        os.chmod(db_path, stat.S_IRUSR | stat.S_IWUSR)  # 0600 permissions
        print("🔒 Database secured with restricted permissions")
    except Exception as e:
        print(f"⚠️  Could not set file permissions: {e}")
        print("    (This is normal on Windows)")
        
    print(f"✅ Database setup complete: {db_path}")
    print("📊 Tables created: window_activity")
    print("🔍 Indexes created: timestamp, app_name, category")

def verify_setup():
    """Verify that everything is set up correctly"""
    # Ensure paths are relative to Observer folder
    current_dir = Path(__file__).parent
    db_path = current_dir / "productivity_data.db"
    config_path = current_dir / "config.json"
    
    # Check database
    if Path(db_path).exists():
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        print(f"✅ Database exists with tables: {tables}")
    else:
        print("❌ Database not found")
        return False
    
    # Check config
    if Path(config_path).exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
        print(f"✅ Config exists with {len(config.get('categories', {}))} categories")
    else:
        print("❌ Config not found")
        return False
    
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("  OBSERVER DATABASE SETUP")
    print("=" * 50)
    
    setup_database()
    
    print("\n" + "-" * 50)
    print("  VERIFICATION")
    print("-" * 50)
    
    if verify_setup():
        print("\n🎉 Observer system is ready to use!")
        print("\nNext steps:")
        print("1. Run: python tracker.py")
        print("2. Run: python server.py")
        print("3. Open: http://localhost:8000/dashboard.html")
    else:
        print("\n❌ Setup incomplete. Check the errors above.")
