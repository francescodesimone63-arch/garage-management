#!/usr/bin/env python3
"""
Script per aggiungere colonne tipo e cellulare alla tabella customers
"""
import sqlite3

db_path = '/Users/francescodesimone/Sviluppo Python/garage-management/backend/garage.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Aggiungi colonna tipo
    cursor.execute("ALTER TABLE customers ADD COLUMN tipo VARCHAR(20) DEFAULT 'privato'")
    print("✅ Colonna 'tipo' aggiunta")
except Exception as e:
    if "duplicate column name" in str(e).lower():
        print("⚠️  Colonna 'tipo' già presente")
    else:
        print(f"❌ Errore aggiunta 'tipo': {e}")

try:
    # Aggiungi colonna cellulare
    cursor.execute("ALTER TABLE customers ADD COLUMN cellulare VARCHAR(20)")
    print("✅ Colonna 'cellulare' aggiunta")
except Exception as e:
    if "duplicate column name" in str(e).lower():
        print("⚠️  Colonna 'cellulare' già presente")
    else:
        print(f"❌ Errore aggiunta 'cellulare': {e}")

try:
    conn.commit()
    print("\n✅ Modifiche salvate!")
    
    # Verifica
    cursor.execute("PRAGMA table_info(customers)")
    columns = cursor.fetchall()
    print("\nColonne tabella customers:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
        
except Exception as e:
    print(f"❌ Errore commit: {e}")
    conn.rollback()
finally:
    conn.close()
