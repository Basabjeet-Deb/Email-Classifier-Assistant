"""
Minimal database module for email analytics.
"""
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

DB_PATH = Path(__file__).parent / "email_analytics.db"


def init_db():
    """Initialize database tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Drop existing tables if they exist
    cursor.execute('DROP TABLE IF EXISTS classifications')
    cursor.execute('DROP TABLE IF EXISTS feedback')
    
    # Classifications table
    cursor.execute('''
        CREATE TABLE classifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id TEXT,
            email_id TEXT,
            category TEXT,
            confidence REAL,
            classifier_used TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Feedback table
    cursor.execute('''
        CREATE TABLE feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_id TEXT,
            predicted_category TEXT,
            correct_category TEXT,
            email_text TEXT,
            confidence REAL,
            classifier_used TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✓ Database initialized with correct schema")


def store_batch_classifications(account_id, emails):
    """Store batch of email classifications."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for email in emails:
        cursor.execute('''
            INSERT INTO classifications (account_id, email_id, category, confidence, classifier_used)
            VALUES (?, ?, ?, ?, ?)
        ''', (account_id, email['id'], email['category'], email['confidence'], email['classifier_used']))
    
    conn.commit()
    conn.close()


def store_feedback(email_id, predicted_category, correct_category, email_text, confidence, classifier_used):
    """Store user feedback."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO feedback (email_id, predicted_category, correct_category, email_text, confidence, classifier_used)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (email_id, predicted_category, correct_category, email_text, confidence, classifier_used))
    
    conn.commit()
    conn.close()


def get_analytics_summary(account_id, days=30):
    """Get comprehensive analytics summary."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    since_date = (datetime.now() - timedelta(days=days)).isoformat()
    
    # Total emails and average confidence
    cursor.execute('''
        SELECT COUNT(*), AVG(confidence)
        FROM classifications
        WHERE account_id = ? AND timestamp >= ?
    ''', (account_id, since_date))
    
    total_emails, avg_confidence = cursor.fetchone()
    total_emails = total_emails or 0
    avg_confidence = round((avg_confidence or 0) * 100, 1)
    
    # Category distribution
    cursor.execute('''
        SELECT category, COUNT(*) as count
        FROM classifications
        WHERE account_id = ? AND timestamp >= ?
        GROUP BY category
        ORDER BY count DESC
    ''', (account_id, since_date))
    
    category_distribution = [
        {'category': row[0], 'count': row[1]}
        for row in cursor.fetchall()
    ]
    
    # Daily trend
    cursor.execute('''
        SELECT DATE(timestamp) as date, COUNT(*) as count
        FROM classifications
        WHERE account_id = ? AND timestamp >= ?
        GROUP BY DATE(timestamp)
        ORDER BY date
    ''', (account_id, since_date))
    
    daily_trend = [
        {'date': row[0], 'count': row[1]}
        for row in cursor.fetchall()
    ]
    
    # Emails by hour (0-23)
    cursor.execute('''
        SELECT CAST(strftime('%H', timestamp) AS INTEGER) as hour, COUNT(*) as count
        FROM classifications
        WHERE account_id = ? AND timestamp >= ?
        GROUP BY hour
    ''', (account_id, since_date))
    
    hour_data = {row[0]: row[1] for row in cursor.fetchall()}
    emails_by_hour = [hour_data.get(h, 0) for h in range(24)]
    
    # Emails by day of week (0=Monday, 6=Sunday)
    cursor.execute('''
        SELECT CAST(strftime('%w', timestamp) AS INTEGER) as dow, COUNT(*) as count
        FROM classifications
        WHERE account_id = ? AND timestamp >= ?
        GROUP BY dow
    ''', (account_id, since_date))
    
    dow_data = {row[0]: row[1] for row in cursor.fetchall()}
    # Convert Sunday=0 to Sunday=6 format
    emails_by_day = [
        dow_data.get(1, 0),  # Monday
        dow_data.get(2, 0),  # Tuesday
        dow_data.get(3, 0),  # Wednesday
        dow_data.get(4, 0),  # Thursday
        dow_data.get(5, 0),  # Friday
        dow_data.get(6, 0),  # Saturday
        dow_data.get(0, 0),  # Sunday
    ]
    
    conn.close()
    
    # Calculate sentiment (simplified based on categories)
    sentiment_positive = sum(
        item['count'] for item in category_distribution 
        if item['category'] in ['Important', 'Social']
    )
    sentiment_negative = sum(
        item['count'] for item in category_distribution 
        if item['category'] in ['Spam']
    )
    sentiment_neutral = total_emails - sentiment_positive - sentiment_negative
    
    return {
        'total_emails': total_emails,
        'average_confidence': avg_confidence,
        'average_processing_time': 45,  # Placeholder - could track this
        'category_distribution': category_distribution,
        'daily_trend': daily_trend,
        'emails_by_hour': emails_by_hour,
        'emails_by_day': emails_by_day,
        'sentiment_distribution': {
            'POSITIVE': sentiment_positive,
            'NEGATIVE': sentiment_negative,
            'NEUTRAL': sentiment_neutral
        }
    }


def get_insights(account_id):
    """Generate AI insights based on email patterns."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    insights = []
    
    # Get total emails
    cursor.execute('SELECT COUNT(*) FROM classifications WHERE account_id = ?', (account_id,))
    total = cursor.fetchone()[0]
    
    if total == 0:
        conn.close()
        return []
    
    # Top category
    cursor.execute('''
        SELECT category, COUNT(*) as count
        FROM classifications
        WHERE account_id = ?
        GROUP BY category
        ORDER BY count DESC
        LIMIT 1
    ''', (account_id,))
    
    top_category = cursor.fetchone()
    if top_category:
        percentage = round((top_category[1] / total) * 100, 1)
        insights.append(f"{top_category[0]} emails make up {percentage}% of your inbox")
    
    # Average confidence
    cursor.execute('SELECT AVG(confidence) FROM classifications WHERE account_id = ?', (account_id,))
    avg_conf = cursor.fetchone()[0]
    if avg_conf:
        avg_conf_pct = round(avg_conf * 100, 1)
        if avg_conf_pct >= 80:
            insights.append(f"High classification confidence at {avg_conf_pct}% - the model is performing well")
        elif avg_conf_pct >= 60:
            insights.append(f"Moderate classification confidence at {avg_conf_pct}% - consider providing feedback")
        else:
            insights.append(f"Low classification confidence at {avg_conf_pct}% - more training data needed")
    
    # Spam detection
    cursor.execute('''
        SELECT COUNT(*) FROM classifications 
        WHERE account_id = ? AND category = 'Spam'
    ''', (account_id,))
    spam_count = cursor.fetchone()[0]
    if spam_count > 0:
        spam_pct = round((spam_count / total) * 100, 1)
        insights.append(f"Detected {spam_count} spam emails ({spam_pct}% of total)")
    
    conn.close()
    return insights


# Initialize database on import
init_db()
