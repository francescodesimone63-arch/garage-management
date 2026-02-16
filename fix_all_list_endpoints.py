#!/usr/bin/env python3
"""
Script per correggere TUTTI gli endpoint GET che restituiscono liste
Aggiunge model_validate() per ogni elemento della lista
"""
import re
from pathlib import Path

endpoints_dir = Path('/Users/francescodesimone/Sviluppo Python/garage-management/backend/app/api/v1/endpoints')

def fix_list_endpoint(filepath):
    """Corregge gli endpoint GET che restituiscono liste"""
    print(f"\n🔍 Analizzando: {filepath.name}")
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Pattern per trovare: "items": variable_list
    pattern = r'("items":\s*)(\w+)(,)'
    
    modified = False
    matches = list(re.finditer(pattern, content))
    
    if not matches:
        print(f"  ⚪ Nessuna lista 'items' trovata")
        return False
    
    for match in reversed(matches):  # Reverse per non alterare indici
        items_str = match.group(1)
        var_name = match.group(2)
        comma = match.group(3)
        
        # Verifica se è già stato corretto
        if '[' in content[max(0, match.start()-50):match.start()]:
            continue
            
        # Cerca il nome dello schema response nelle righe precedenti
        lines_before = content[:match.start()].split('\n')
        response_schema = None
        
        for line in reversed(lines_before[-30:]):
            if '@router.get' in line and 'response_model=' in line:
                # Non ha response_model per liste, cerchiamo nel file
                break
        
        # Cerca import dello schema Response
        imports = content.split('\n')[:50]
        schema_names = []
        for imp in imports:
            if 'Response' in imp and 'from app.schemas' in imp:
                # Estrai i nomi degli schema
                match_schema = re.findall(r'(\w+Response)', imp)
                schema_names.extend(match_schema)
        
        # Deduce schema name dal nome variabile o filename
        if var_name.endswith('s'):
            singular = var_name[:-1]  # rimuovi 's' finale
            for schema in schema_names:
                if singular.lower() in schema.lower():
                    response_schema = schema
                    break
        
        if not response_schema and schema_names:
            # Usa il primo disponibile
            response_schema = schema_names[0]
        
        if response_schema:
            # Sostituisci
            new_items = f'{items_str}[{response_schema}.model_validate(x) for x in {var_name}]{comma}'
            content = content[:match.start()] + new_items + content[match.end():]
            print(f"  ✅ Corretto: 'items': {var_name} -> List[{response_schema}].model_validate()")
            modified = True
    
    if modified:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"  💾 File salvato")
        return True
    else:
        print(f"  ⚪ Già corretto o non necessario")
        return False

# Files da verificare
all_files = [
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

print("=" * 70)
print("🔧 CORREZIONE LISTE GET - TUTTI GLI ENDPOINT")
print("=" * 70)

fixed_count = 0
for filename in all_files:
    filepath = endpoints_dir / filename
    if filepath.exists():
        if fix_list_endpoint(filepath):
            fixed_count += 1
    else:
        print(f"\n⚠️  File non trovato: {filename}")

print("\n" + "=" * 70)
print(f"✅ COMPLETATO! Files modificati: {fixed_count}/{len(all_files)}")
print("=" * 70)
