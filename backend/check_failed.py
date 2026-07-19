import sqlite3

conn = sqlite3.connect("medflow.db")
cur = conn.cursor()
cur.execute(
    "SELECT filename, status, raw_text, created_at FROM documents "
    "WHERE status='failed' ORDER BY created_at DESC LIMIT 1"
)
row = cur.fetchone()

if not row:
    print("No failed documents found.")
else:
    filename, status, raw_text, created_at = row
    print("Most recent failure:")
    print(f"File:    {filename}")
    print(f"When:    {created_at}")
    print(f"Status:  {status}")
    print(f"Error:   {raw_text}")