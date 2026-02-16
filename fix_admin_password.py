#!/usr/bin/env python3
"""
Script per aggiornare password admin
"""
import sqlite3

# Hash bcrypt per "admin123"
correct_hash = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"

# Connetti al database
conn = sqlite3.connect('/Users/francescodesimone/Sviluppo Python/garage-management/backend/garage.db')
cursor = conn.cursor()

try:
    # Aggiorna password
    cursor.execute(
        "UPDATE users SET password_hash = ? WHERE username = 'admin'",
        (correct_hash,)
    )
    
    conn.commit()
    
    # Verifica
    cursor.execute("SELECT username, email, attivo FROM users WHERE username = 'admin'")
    result = cursor.fetchone()
    
    if result:
        print("✅ Password aggiornata con successo!")
        print(f"   Username: {result[0]}")
        print(f"   Email: {result[1]}")
        print(f"   Attivo: {result[2]}")
        print(f"   Password: admin123")
    else:
        print("❌ Utente admin non trovato!")
        
except Exception as e:
    print(f"❌ Errore: {e}")
    conn.rollback()
finally:
    conn.close()
