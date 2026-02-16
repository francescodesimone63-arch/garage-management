#!/usr/bin/env python3
import sqlite3

new_hash = "$2b$12$F/lP4u9eLH5VAn7MygHine74Ydd.3OCHkgt2alUPCL5yhpSEiB/JW"

conn = sqlite3.connect('/Users/francescodesimone/Sviluppo Python/garage-management/backend/garage.db')
cursor = conn.cursor()

try:
    cursor.execute("UPDATE users SET password_hash = ? WHERE username = 'admin'", (new_hash,))
    conn.commit()
    print("✅ Password aggiornata!")
    print("   Email: admin@garage.local")
    print("   Password: admin123")
except Exception as e:
    print(f"❌ Errore: {e}")
    conn.rollback()
finally:
    conn.close()
