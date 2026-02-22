"""
Database module for storing email classification history and analytics.
Uses SQLite for lightweight, serverless data storage.
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "email_analytics.db")

def init_database():
    """Initialize the database with required tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create classifications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS classifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id TEXT NOT NULL,
            message_id TEXT NOT NULL,
            sender TEXT NOT NULL,
            sender_domain TEXT,
            subject TEXT NOT NULL,
            category TEXT NOT NULL,
            confidence REAL NOT NULL,
            sentiment TEXT,
            sentiment_score REAL,
            method TEXT,
            processing_time_ms REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            date_only DATE,
            hour INTEGER,
            day_of_week INTEGER
        )
    ''')
    
    # Create indexes for faster queries
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_account ON classifications(account_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON classifications(category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON classifications(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON classifications(date_only)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sender ON classifications(sender_domain)')
    
    conn.commit()
    conn.close()

def store_classification(account_id: str, email_data: Dict[str, Any]):
    """Store a single email classification in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Extract timestamp components
    now = datetime.now()
    date_only = now.date()
    hour = now.hour
    day_of_week = now.weekday()  # 0=Monday, 6=Sunday
    
    # Extract sender domain
    sender = email_data.get('sender', '')
    sender_domain = sender.split('@')[-1].split('>')[0].strip() if '@' in sender else 'unknown'
    
    cursor.execute('''
        INSERT INTO classifications 
        (account_id, message_id, sender, sender_domain, subject, category, 
         confidence, sentiment, sentiment_score, method, processing_time_ms,
         date_only, hour, day_of_week)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        account_id,
        email_data.get('id', ''),
        sender,
        sender_domain,
        email_data.get('subject', ''),
        email_data.get('category', 'Other'),
        email_data.get('confidence', 0.0),
        email_data.get('sentiment', 'NEUTRAL'),
        email_data.get('sentiment_score', 0.0),
        email_data.get('method', 'unknown'),
        email_data.get('processing_time_ms', 0.0),
        date_only,
        hour,
        day_of_week
    ))
    
    conn.commit()
    conn.close()

def store_batch_classifications(account_id: str, emails: List[Dict[str, Any]]):
    """Store multiple email classifications in batch."""
    for email in emails:
        store_classification(account_id, email)

def get_analytics_summary(account_id: str, days: int = 30) -> Dict[str, Any]:
    """Get comprehensive analytics summary for the dashboard."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Date filter
    date_filter = f"AND date_only >= date('now', '-{days} days')" if days > 0 else ""
    
    # Total emails
    cursor.execute(f'''
        SELECT COUNT(*) FROM classifications 
        WHERE account_id = ? {date_filter}
    ''', (account_id,))
    total_emails = cursor.fetchone()[0]
    
    # Category distribution
    cursor.execute(f'''
        SELECT category, COUNT(*) as count, AVG(confidence) as avg_conf
        FROM classifications 
        WHERE account_id = ? {date_filter}
        GROUP BY category
        ORDER BY count DESC
    ''', (account_id,))
    category_dist = [
        {"category": row[0], "count": row[1], "avg_confidence": round(row[2], 2)}
        for row in cursor.fetchall()
    ]
    
    # Top senders
    cursor.execute(f'''
        SELECT sender_domain, COUNT(*) as count
        FROM classifications 
        WHERE account_id = ? {date_filter}
        GROUP BY sender_domain
        ORDER BY count DESC
        LIMIT 10
    ''', (account_id,))
    top_senders = [
        {"sender": row[0], "count": row[1]}
        for row in cursor.fetchall()
    ]
    
    # Emails by hour
    cursor.execute(f'''
        SELECT hour, COUNT(*) as count
        FROM classifications 
        WHERE account_id = ? {date_filter}
        GROUP BY hour
        ORDER BY hour
    ''', (account_id,))
    hourly_data = {row[0]: row[1] for row in cursor.fetchall()}
    emails_by_hour = [hourly_data.get(h, 0) for h in range(24)]
    
    # Emails by day of week
    cursor.execute(f'''
        SELECT day_of_week, COUNT(*) as count
        FROM classifications 
        WHERE account_id = ? {date_filter}
        GROUP BY day_of_week
        ORDER BY day_of_week
    ''', (account_id,))
    weekly_data = {row[0]: row[1] for row in cursor.fetchall()}
    emails_by_day = [weekly_data.get(d, 0) for d in range(7)]
    
    # Sentiment distribution
    cursor.execute(f'''
        SELECT sentiment, COUNT(*) as count
        FROM classifications 
        WHERE account_id = ? {date_filter}
        GROUP BY sentiment
    ''', (account_id,))
    sentiment_dist = {row[0]: row[1] for row in cursor.fetchall()}
    
    # Method distribution
    cursor.execute(f'''
        SELECT method, COUNT(*) as count
        FROM classifications 
        WHERE account_id = ? {date_filter}
        GROUP BY method
    ''', (account_id,))
    method_dist = {row[0]: row[1] for row in cursor.fetchall()}
    
    # Average metrics
    cursor.execute(f'''
        SELECT 
            AVG(confidence) as avg_conf,
            AVG(processing_time_ms) as avg_time,
            AVG(sentiment_score) as avg_sentiment
        FROM classifications 
        WHERE account_id = ? {date_filter}
    ''', (account_id,))
    avg_row = cursor.fetchone()
    
    # Daily trend (last 30 days)
    cursor.execute(f'''
        SELECT date_only, COUNT(*) as count
        FROM classifications 
        WHERE account_id = ? AND date_only >= date('now', '-30 days')
        GROUP BY date_only
        ORDER BY date_only
    ''', (account_id,))
    daily_trend = [
        {"date": row[0], "count": row[1]}
        for row in cursor.fetchall()
    ]
    
    conn.close()
    
    return {
        "total_emails": total_emails,
        "category_distribution": category_dist,
        "top_senders": top_senders,
        "emails_by_hour": emails_by_hour,
        "emails_by_day": emails_by_day,
        "sentiment_distribution": sentiment_dist,
        "method_distribution": method_dist,
        "average_confidence": round(avg_row[0], 2) if avg_row[0] else 0,
        "average_processing_time": round(avg_row[1], 2) if avg_row[1] else 0,
        "average_sentiment_score": round(avg_row[2], 2) if avg_row[2] else 0,
        "daily_trend": daily_trend,
        "days_analyzed": days
    }

def get_insights(account_id: str) -> List[str]:
    """Generate AI-powered insights from the data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    insights = []
    
    # Most active day
    cursor.execute('''
        SELECT day_of_week, COUNT(*) as count
        FROM classifications 
        WHERE account_id = ?
        GROUP BY day_of_week
        ORDER BY count DESC
        LIMIT 1
    ''', (account_id,))
    result = cursor.fetchone()
    if result:
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        insights.append(f"Your busiest day is {days[result[0]]} with {result[1]} emails on average")
    
    # Most active hour
    cursor.execute('''
        SELECT hour, COUNT(*) as count
        FROM classifications 
        WHERE account_id = ?
        GROUP BY hour
        ORDER BY count DESC
        LIMIT 1
    ''', (account_id,))
    result = cursor.fetchone()
    if result:
        hour = result[0]
        period = "AM" if hour < 12 else "PM"
        display_hour = hour if hour <= 12 else hour - 12
        if display_hour == 0:
            display_hour = 12
        insights.append(f"Peak email time is {display_hour}:00 {period} with {result[1]} emails")
    
    # Spam percentage
    cursor.execute('''
        SELECT 
            SUM(CASE WHEN category = 'Spam/Promotional' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as spam_pct
        FROM classifications 
        WHERE account_id = ?
    ''', (account_id,))
    result = cursor.fetchone()
    if result and result[0]:
        spam_pct = round(result[0], 1)
        if spam_pct > 50:
            insights.append(f"{spam_pct}% of your emails are spam - consider unsubscribing from newsletters")
        else:
            insights.append(f"Only {spam_pct}% spam - your inbox is well-managed")
    
    # Top sender
    cursor.execute('''
        SELECT sender_domain, COUNT(*) as count
        FROM classifications 
        WHERE account_id = ?
        GROUP BY sender_domain
        ORDER BY count DESC
        LIMIT 1
    ''', (account_id,))
    result = cursor.fetchone()
    if result:
        insights.append(f"Most frequent sender: {result[0]} ({result[1]} emails)")
    
    # Sentiment insight
    cursor.execute('''
        SELECT 
            SUM(CASE WHEN sentiment = 'NEGATIVE' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as neg_pct
        FROM classifications 
        WHERE account_id = ?
    ''', (account_id,))
    result = cursor.fetchone()
    if result and result[0]:
        neg_pct = round(result[0], 1)
        if neg_pct > 30:
            insights.append(f"{neg_pct}% of emails have negative sentiment - high stress indicator")
        else:
            insights.append(f"Positive inbox mood - only {neg_pct}% negative emails")
    
    conn.close()
    return insights

# Initialize database on module import
init_database()
