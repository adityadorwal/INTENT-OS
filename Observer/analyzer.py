#!/usr/bin/env python3
"""
Productivity Tracker - Data Analyzer
Generates insights and reports from tracked data
"""

import sqlite3
import json
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path


class ProductivityAnalyzer:
    def __init__(self, db_path="productivity_data.db"):
        # Use Observer folder database (actual location)
        current_dir = Path(__file__).parent
        if not Path(db_path).is_absolute():
            self.db_path = current_dir / db_path
        else:
            self.db_path = Path(db_path)
        
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def get_daily_stats(self, date=None):
        """Get statistics for a specific day"""
        if date is None:
            date = datetime.now().date()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get all activities for the day
        cursor.execute("""
            SELECT 
                app_name,
                category,
                is_productive,
                SUM(duration_seconds) as total_time,
                COUNT(*) as activity_count
            FROM window_activity
            WHERE DATE(timestamp) = ?
            GROUP BY app_name, category, is_productive
            ORDER BY total_time DESC
        """, (date,))
        
        activities = cursor.fetchall()
        
        # Calculate totals
        total_time = sum(row[3] for row in activities)
        productive_time = sum(row[3] for row in activities if row[2])
        
        productivity_score = (productive_time / total_time * 100) if total_time > 0 else 0
        
        # Top apps
        top_apps = [
            {
                "app": row[0],
                "category": row[1],
                "time_seconds": row[3],
                "time_formatted": self.format_duration(row[3]),
                "percentage": (row[3] / total_time * 100) if total_time > 0 else 0
            }
            for row in activities[:10]
        ]
        
        conn.close()
        
        return {
            "date": str(date),
            "total_time_seconds": total_time,
            "total_time_formatted": self.format_duration(total_time),
            "productive_time_seconds": productive_time,
            "productive_time_formatted": self.format_duration(productive_time),
            "productivity_score": round(productivity_score, 2),
            "top_apps": top_apps,
            "activity_count": len(activities)
        }
    
    def get_weekly_stats(self, end_date=None):
        """Get statistics for the past 7 days"""
        if end_date is None:
            end_date = datetime.now().date()
        
        start_date = end_date - timedelta(days=6)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get daily breakdown
        daily_data = []
        for i in range(7):
            current_date = start_date + timedelta(days=i)
            day_stats = self.get_daily_stats(current_date)
            daily_data.append(day_stats)
        
        # Calculate weekly totals
        total_time = sum(day['total_time_seconds'] for day in daily_data)
        productive_time = sum(day['productive_time_seconds'] for day in daily_data)
        avg_productivity = sum(day['productivity_score'] for day in daily_data) / 7
        
        # Get top apps for the week
        cursor.execute("""
            SELECT 
                app_name,
                category,
                SUM(duration_seconds) as total_time
            FROM window_activity
            WHERE DATE(timestamp) BETWEEN ? AND ?
            GROUP BY app_name, category
            ORDER BY total_time DESC
            LIMIT 10
        """, (start_date, end_date))
        
        top_apps_week = [
            {
                "app": row[0],
                "category": row[1],
                "time_seconds": row[2],
                "time_formatted": self.format_duration(row[2])
            }
            for row in cursor.fetchall()
        ]
        
        conn.close()
        
        return {
            "period": f"{start_date} to {end_date}",
            "total_time_seconds": total_time,
            "total_time_formatted": self.format_duration(total_time),
            "productive_time_seconds": productive_time,
            "productive_time_formatted": self.format_duration(productive_time),
            "average_productivity_score": round(avg_productivity, 2),
            "daily_breakdown": daily_data,
            "top_apps": top_apps_week
        }
    
    def get_monthly_stats(self, year=None, month=None):
        """Get statistics for a specific month"""
        if year is None or month is None:
            now = datetime.now()
            year = now.year
            month = now.month
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get all data for the month
        cursor.execute("""
            SELECT 
                DATE(timestamp) as date,
                SUM(duration_seconds) as total_time,
                SUM(CASE WHEN is_productive = 1 THEN duration_seconds ELSE 0 END) as productive_time
            FROM window_activity
            WHERE strftime('%Y', timestamp) = ? AND strftime('%m', timestamp) = ?
            GROUP BY DATE(timestamp)
            ORDER BY date
        """, (str(year), str(month).zfill(2)))
        
        daily_data = cursor.fetchall()
        
        total_time = sum(row[1] for row in daily_data)
        productive_time = sum(row[2] for row in daily_data)
        productivity_score = (productive_time / total_time * 100) if total_time > 0 else 0
        
        # Get category breakdown
        cursor.execute("""
            SELECT 
                category,
                SUM(duration_seconds) as total_time
            FROM window_activity
            WHERE strftime('%Y', timestamp) = ? AND strftime('%m', timestamp) = ?
            GROUP BY category
            ORDER BY total_time DESC
        """, (str(year), str(month).zfill(2)))
        
        categories = [
            {
                "category": row[0],
                "time_seconds": row[1],
                "time_formatted": self.format_duration(row[1]),
                "percentage": (row[1] / total_time * 100) if total_time > 0 else 0
            }
            for row in cursor.fetchall()
        ]
        
        conn.close()
        
        return {
            "year": year,
            "month": month,
            "total_days": len(daily_data),
            "total_time_seconds": total_time,
            "total_time_formatted": self.format_duration(total_time),
            "productive_time_seconds": productive_time,
            "productive_time_formatted": self.format_duration(productive_time),
            "productivity_score": round(productivity_score, 2),
            "categories": categories,
            "daily_data": [
                {
                    "date": row[0],
                    "total_time": row[1],
                    "productive_time": row[2],
                    "productivity_score": (row[2] / row[1] * 100) if row[1] > 0 else 0
                }
                for row in daily_data
            ]
        }
    
    def get_overall_stats(self):
        """Get all-time statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get overall totals
        cursor.execute("""
            SELECT 
                SUM(duration_seconds) as total_time,
                SUM(CASE WHEN is_productive = 1 THEN duration_seconds ELSE 0 END) as productive_time,
                MIN(DATE(timestamp)) as first_day,
                MAX(DATE(timestamp)) as last_day,
                COUNT(DISTINCT DATE(timestamp)) as total_days
            FROM window_activity
        """)
        
        row = cursor.fetchone()
        total_time = row[0] or 0
        productive_time = row[1] or 0
        first_day = row[2]
        last_day = row[3]
        total_days = row[4] or 0
        
        productivity_score = (productive_time / total_time * 100) if total_time > 0 else 0
        
        # Get most productive day
        cursor.execute("""
            SELECT 
                DATE(timestamp) as date,
                SUM(duration_seconds) as total_time,
                SUM(CASE WHEN is_productive = 1 THEN duration_seconds ELSE 0 END) as productive_time
            FROM window_activity
            GROUP BY DATE(timestamp)
            ORDER BY productive_time DESC
            LIMIT 1
        """)
        
        best_day_row = cursor.fetchone()
        best_day = {
            "date": best_day_row[0] if best_day_row else None,
            "productive_time": best_day_row[2] if best_day_row else 0,
            "productive_time_formatted": self.format_duration(best_day_row[2]) if best_day_row else "0h"
        }
        
        # Get all-time top apps
        cursor.execute("""
            SELECT 
                app_name,
                category,
                SUM(duration_seconds) as total_time
            FROM window_activity
            GROUP BY app_name, category
            ORDER BY total_time DESC
            LIMIT 15
        """)
        
        top_apps = [
            {
                "app": row[0],
                "category": row[1],
                "time_seconds": row[2],
                "time_formatted": self.format_duration(row[2])
            }
            for row in cursor.fetchall()
        ]
        
        conn.close()
        
        return {
            "first_tracked_day": first_day,
            "last_tracked_day": last_day,
            "total_days_tracked": total_days,
            "total_time_seconds": total_time,
            "total_time_formatted": self.format_duration(total_time),
            "productive_time_seconds": productive_time,
            "productive_time_formatted": self.format_duration(productive_time),
            "overall_productivity_score": round(productivity_score, 2),
            "best_day": best_day,
            "top_apps_alltime": top_apps
        }
    
    def get_hourly_breakdown(self, date=None):
        """Get productivity breakdown by hour of day"""
        if date is None:
            date = datetime.now().date()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                CAST(strftime('%H', timestamp) AS INTEGER) as hour,
                SUM(duration_seconds) as total_time,
                SUM(CASE WHEN is_productive = 1 THEN duration_seconds ELSE 0 END) as productive_time
            FROM window_activity
            WHERE DATE(timestamp) = ?
            GROUP BY hour
            ORDER BY hour
        """, (date,))
        
        hourly_data = {}
        for row in cursor.fetchall():
            hour = row[0]
            hourly_data[hour] = {
                "hour": hour,
                "total_time": row[1],
                "productive_time": row[2],
                "productivity_score": (row[2] / row[1] * 100) if row[1] > 0 else 0
            }
        
        # Fill in missing hours with zeros
        result = []
        for hour in range(24):
            if hour in hourly_data:
                result.append(hourly_data[hour])
            else:
                result.append({
                    "hour": hour,
                    "total_time": 0,
                    "productive_time": 0,
                    "productivity_score": 0
                })
        
        conn.close()
        return result
    
    def format_duration(self, seconds):
        """Format seconds into human-readable duration"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes}m"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m"
    
    def generate_report(self, report_type="daily", output_file=None):
        """Generate a complete report"""
        if report_type == "daily":
            data = self.get_daily_stats()
        elif report_type == "weekly":
            data = self.get_weekly_stats()
        elif report_type == "monthly":
            data = self.get_monthly_stats()
        elif report_type == "overall":
            data = self.get_overall_stats()
        else:
            return {"error": "Invalid report type"}
        
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"✓ Report saved to: {output_file}")
        
        return data
    
    def print_daily_summary(self):
        """Print a formatted daily summary to console"""
        stats = self.get_daily_stats()
        
        print("\n" + "=" * 60)
        print(f"  DAILY PRODUCTIVITY REPORT - {stats['date']}")
        print("=" * 60)
        print(f"\n⏱️  Total Time Tracked: {stats['total_time_formatted']}")
        print(f"✅ Productive Time: {stats['productive_time_formatted']}")
        print(f"📊 Productivity Score: {stats['productivity_score']}%")
        print(f"\n🔝 Top Applications:")
        
        for i, app in enumerate(stats['top_apps'][:5], 1):
            print(f"   {i}. {app['app']:<20} {app['time_formatted']:<10} ({app['percentage']:.1f}%)")
        
        print("=" * 60 + "\n")


def main():
    """Main entry point for analyzer"""
    import sys
    
    analyzer = ProductivityAnalyzer()
    
    if len(sys.argv) > 1:
        report_type = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        analyzer.generate_report(report_type, output_file)
    else:
        # Default: show today's summary
        analyzer.print_daily_summary()


if __name__ == "__main__":
    main()
