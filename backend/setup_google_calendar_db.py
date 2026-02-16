#!/usr/bin/env python3
"""
Setup Google Calendar database schema
"""
import sqlite3
import sys

def setup_database():
    conn = sqlite3.connect("garage.db")
    cursor = conn.cursor()
    
    try:
        # Add google_event_id column to work_orders
        cursor.execute("ALTER TABLE work_orders ADD COLUMN google_event_id TEXT")
        print("✅ Added google_event_id column to work_orders")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e):
            print("ℹ️  google_event_id column already exists")
        else:
            print(f"❌ Error adding google_event_id: {e}")
            return False
    
    # Create index
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_work_orders_google_event_id ON work_orders(google_event_id)")
    print("✅ Created index on google_event_id")
    
    # Create google_oauth_tokens table
    create_table = """
    CREATE TABLE IF NOT EXISTS google_oauth_tokens (
        id INTEGER PRIMARY KEY,
        refresh_token TEXT NOT NULL,
        access_token TEXT,
        access_token_expiry DATETIME,
        calendar_id TEXT NOT NULL DEFAULT 'primary',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """
    cursor.execute(create_table)
    print("✅ Created google_oauth_tokens table")
    
    # Create index
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_google_oauth_tokens_id ON google_oauth_tokens(id)")
    print("✅ Created index on google_oauth_tokens")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Database schema updated successfully!")
    return True

if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)
