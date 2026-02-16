#!/usr/bin/env python3
"""
Script per correggere la serializzazione Pydantic v2 in tutti gli endpoint
Sostituisce 'return object' con 'return Schema.model_validate(object)'
"""
import re
import os
from pathlib import Path

# Directory degli endpoint
endpoints_dir = Path('/Users/francescodesimone/Sviluppo Python/garage-management/backend/app/api/v1/endpoints')

# Pattern da cercare: return seguito da un oggetto (non dict, non lista)
# Escludi: return None, return {}, return [], return dict(), ecc.
pattern_return = r'(\s+)return\s+(\w+)\s*$'

# File da correggere (esclusi quelli già corretti)
files_to_fix = [
    'work_orders.py',
    'parts.py',
    'tires.py',
    'courtesy_cars.py',
    'maintenance_schedules.py',
    'documents.py',
    'notifications.py',
    'calendar_events.py',
    'activity_logs.py',
    'users.py'
]

# Mapping nome variabile -> Response schema (pattern comuni)
schema_mapping = {
    'work_order': 'WorkOrderResponse',
    'part': 'PartResponse',
    'tire': 'TireResponse',
    'courtesy_car': 'CourtesyCarResponse',
    'schedule': 'MaintenanceScheduleResponse',
    'document': 'DocumentResponse',
    'notification': 'NotificationResponse',
    'event': 'CalendarEventResponse',
    'log': 'ActivityLogResponse',
    'user': 'UserResponse',
}

def fix_file(filepath):
    """Corregge un file aggiungendo model_validate()"""
    print(f"\n🔍 Analizzando: {filepath.name}")
    
    with open(filepath, 'r') as f:
        content = f.read()
        lines = content.split('\n')
    
    modified = False
    new_lines = []
    
    for i, line in enumerate(lines):
        # Cerca pattern 'return object'
        match = re.search(pattern_return, line)
        
        if match:
            indent = match.group(1)
            var_name = match.group(2)
            
            # Escludi casi specali
            if var_name in ['None', 'dict', 'list', 'True', 'False']:
                new_lines.append(line)
                continue
            
            # Cerca la funzione che contiene questo return
            func_line = None
            for j in range(i-1, max(0, i-50), -1):
                if 'def ' in lines[j] and 'response_model=' in lines[j]:
                    func_line = lines[j]
                    break
            
            if func_line:
                # Estrai il response_model
                response_match = re.search(r'response_model=(\w+)', func_line)
                if response_match:
                    response_schema = response_match.group(1)
                    
                    # Verifica che non sia già corretto
                    if 'model_validate' not in line:
                        new_line = f"{indent}return {response_schema}.model_validate({var_name})"
                        print(f"  ✅ Line {i+1}: {line.strip()} -> {new_line.strip()}")
                        new_lines.append(new_line)
                        modified = True
                        continue
        
        new_lines.append(line)
    
    if modified:
        # Salva il file modificato
        with open(filepath, 'w') as f:
            f.write('\n'.join(new_lines))
        print(f"  💾 File salvato con le modifiche")
        return True
    else:
        print(f"  ⚪ Nessuna modifica necessaria")
        return False

# Main
print("=" * 70)
print("🔧 CORREZIONE SERIALIZZAZIONE PYDANTIC V2 - TUTTI GLI ENDPOINT")
print("=" * 70)

fixed_count = 0
for filename in files_to_fix:
    filepath = endpoints_dir / filename
    if filepath.exists():
        if fix_file(filepath):
            fixed_count += 1
    else:
        print(f"\n⚠️  File non trovato: {filename}")

print("\n" + "=" * 70)
print(f"✅ COMPLETATO! Files modificati: {fixed_count}/{len(files_to_fix)}")
print("=" * 70)
