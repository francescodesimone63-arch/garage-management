#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('db.sqlite3')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Verifica il numero di auto totali
cursor.execute("SELECT COUNT(*) FROM vehicles")
total = cursor.fetchone()[0]
print(f"📊 Totale auto nel database: {total}")

# Verifica auto con courtesy_car = true
cursor.execute("SELECT COUNT(*) FROM vehicles WHERE courtesy_car = 1")
courtesy_true = cursor.fetchone()[0]
print(f"✅ Auto con courtesy_car = true: {courtesy_true}")

# Verifica auto con courtesy_car = false
cursor.execute("SELECT COUNT(*) FROM vehicles WHERE courtesy_car = 0 OR courtesy_car IS NULL")
not_courtesy = cursor.fetchone()[0]
print(f"❌ Auto con courtesy_car = false/null: {not_courtesy}")

# Mostra prime 20 auto
print("\n📋 Campione auto nel database:")
cursor.execute("""
    SELECT id, targa, marca, modello, courtesy_car, disponibile
    FROM vehicles
    LIMIT 20
""")
for row in cursor.fetchall():
    courtesy = "✅" if row['courtesy_car'] else "❌"
    disponibile = "✅" if row['disponibile'] else "❌"
    print(f"  ID: {row['id']:3} | {row['targa']:8} | {row['marca']} {row['modello']:15} | Cortesia: {courtesy} | Disponibile: {disponibile}")

conn.close()
