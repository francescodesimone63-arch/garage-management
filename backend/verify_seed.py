#!/usr/bin/env python3
"""Verifica dati caricati nel database"""
import sqlite3
import sys

db_path = "/Users/francescodesimone/Sviluppo Python/garage-management/backend/garage.db"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("📊 DATI CARICATI NEL DATABASE")
    print("="*60)
    
    tables = {
        'Utenti': 'users',
        'Clienti': 'customers',
        'Veicoli': 'vehicles',
        'Schede Lavoro': 'work_orders',
        'Permessi': 'permissions',
        'Ruoli-Permessi': 'role_permissions',
        'Officine': 'workshops',
        'Rami Sinistro': 'insurance_branch_types',
        'Stati Intervento': 'intervention_status_types',
    }
    
    total = 0
    for label, table_name in tables.items():
        count = cursor.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        total += count
        status = "✅" if count > 0 else "⚠️"
        print(f"{status} {label:25s}: {count:4d} record")
    
    print("="*60)
    print(f"📈 TOTALE RECORD NEL DB: {total}")
    print("="*60)
    print("\n🎉 DATABASE POPOPOLATO CORRETTAMENTE!\n")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Errore: {e}", file=sys.stderr)
    sys.exit(1)
