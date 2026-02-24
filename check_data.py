import sqlite3

conn = sqlite3.connect('email_analytics.db')
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM classifications WHERE confidence > 0.7')
count = cursor.fetchone()[0]
print(f'High-confidence emails in database: {count}')

if count > 0:
    cursor.execute('SELECT category, COUNT(*) FROM classifications WHERE confidence > 0.7 GROUP BY category')
    print('\nBy category:')
    for row in cursor.fetchall():
        print(f'  {row[0]}: {row[1]}')
    
    if count >= 50:
        print(f'\n✅ Enough data to retrain! ({count} emails)')
    else:
        print(f'\n⚠️ Need more data. Have {count}, need 50+')
else:
    print('\n❌ No data yet. Run a scan first.')

conn.close()
