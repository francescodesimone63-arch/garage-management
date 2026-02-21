#!/usr/bin/env python3
"""
FASE 5: Script per proteggere tutti gli endpoint con permission checking
Questo script aggiunge @Depends(require_permission(...)) a tutti gli endpoint
"""

import re
import os
from pathlib import Path

# Definizione delle protezioni per endpoint
ENDPOINT_PROTECTIONS = {
    # Customers - 5 permission levels
    "customers.py": {
        'read_customers': 'customers.view',
        'create_customer': 'customers.create',
        'read_customer': 'customers.view',
        'read_customer_with_vehicles': 'customers.view',
        'read_customer_stats': 'customers.view',
        'update_customer': 'customers.edit',
        'delete_customer': 'customers.delete',
    },
    
    # Vehicles
    "vehicles.py": {
        'list_vehicles': 'vehicles.view',
        'create_vehicle': 'vehicles.create',
        'get_vehicle': 'vehicles.view',
        'update_vehicle': 'vehicles.edit',
        'delete_vehicle': 'vehicles.delete',
    },
    
    # Work Orders
    "work_orders.py": {
        'read_work_orders': 'work_orders.view',
        'create_work_order': 'work_orders.create',
        'read_work_order': 'work_orders.view',
        'update_work_order': 'work_orders.edit',
        'delete_work_order': 'work_orders.delete',
        'change_work_order_status': 'work_orders.approve',
        'approve_work_order': 'work_orders.approve',
    },
    
    # Users (admin only)
    "users.py": {
        'list_users': 'system.manage_users',
        'create_user': 'system.manage_users',
        'get_user': 'system.manage_users',
        'update_user': 'system.manage_users',
        'delete_user': 'system.manage_users',
    },
    
    # Courtesy Cars
    "courtesy_cars.py": {
        'read_courtesy_cars': 'courtesy_cars.view',
        'create_courtesy_car': 'courtesy_cars.create',
        'get_available_cars': 'courtesy_cars.view',
        'get_courtesy_car': 'courtesy_cars.view',
        'update_courtesy_car': 'courtesy_cars.edit',
        'delete_courtesy_car': 'courtesy_cars.delete',
        'loan_courtesy_car': 'courtesy_cars.loan',
        'return_courtesy_car': 'courtesy_cars.return',
        'maintenance_courtesy_car': 'courtesy_cars.edit',
    },
    
    # Documents
    "documents.py": {
        'read_documents': 'documents.view',
        'create_document': 'documents.create',
        'upload_document': 'documents.create',
        'get_document': 'documents.view',
    },
    
    # Parts
    "parts.py": {
        'list_parts': 'parts.view',
        'create_part': 'parts.create',
        'get_part': 'parts.view',
        'update_part': 'parts.edit',
        'delete_part': 'parts.delete',
    },
    
    # Tires
    "tires.py": {
        'list_tires': 'tires.view',
        'create_tire': 'tires.create',
        'get_tire': 'tires.view',
        'update_tire': 'tires.edit',
        'delete_tire': 'tires.delete',
    },
    
    # Calendar
    "calendar.py": {
        'get_calendar_events': 'calendar.view',
        'create_event': 'calendar.create',
        'update_event': 'calendar.edit',
        'delete_event': 'calendar.delete',
    },
    
    # Interventions
    "interventions.py": {
        'list_interventions': 'interventions.view',
        'create_intervention': 'interventions.create',
        'get_intervention': 'interventions.view',
        'update_intervention': 'interventions.edit',
    },
    
    # Dashboard (view only)
    "dashboard.py": {
        'get_dashboard': 'dashboard.view',
        'get_summary': 'dashboard.view',
    },
    
    # Activity Logs (view only)
    "activity_logs.py": {
        'list_logs': 'activity_logs.view',
        'get_log': 'activity_logs.view',
    },
    
    # Maintenance Schedules
    "maintenance_schedules.py": {
        'list_schedules': 'maintenance_schedules.view',
        'create_schedule': 'maintenance_schedules.create',
        'get_schedule': 'maintenance_schedules.view',
        'update_schedule': 'maintenance_schedules.edit',
        'delete_schedule': 'maintenance_schedules.delete',
    },
    
    # CMM (Capo Meccanica)
    "cmm.py": {
        'get_dashboard': 'workshop.view',
        'get_stats': 'workshop.view',
    },
    
    # Notifications
    "notifications.py": {
        'list_notifications': 'notifications.view',
        'mark_read': 'notifications.edit',
    },
}

# Files to skip protection
SKIP_FILES = {'auth.py', 'google_oauth.py', '__init__.py', '__pycache__'}


def get_endpoints_dir():
    """Get the endpoints directory path"""
    current = Path(__file__).parent
    endpoints = current / 'backend' / 'app' / 'api' / 'v1' / 'endpoints'
    if not endpoints.exists():
        # Try relative to current working directory
        endpoints = Path.cwd() / 'backend' / 'app' / 'api' / 'v1' / 'endpoints'
    return endpoints


def extract_function_name(def_line):
    """Extract function name from 'def function_name(' line"""
    match = re.search(r'def\s+(\w+)\s*\(', def_line)
    if match:
        return match.group(1)
    return None


def needs_permission_import(content):
    """Check if file needs permission imports"""
    return 'from app.core.permissions import' not in content


def add_permission_import(content):
    """Add permission imports if not present"""
    if needs_permission_import(content):
        # Find the import section
        lines = content.split('\n')
        insert_pos = 0
        
        # Find where to insert (after other app imports)
        for i, line in enumerate(lines):
            if line.startswith('from app.'):
                insert_pos = i + 1
        
        new_import = 'from app.core.permissions import require_permission'
        lines.insert(insert_pos, new_import)
        content = '\n'.join(lines)
    
    return content


def protect_endpoint(function_def, permission_code):
    """Add @Depends(require_permission(...)) to a function"""
    # Check if already has dependencies
    lines = function_def.split('\n')
    
    # Find the function signature line
    func_line_idx = -1
    for i, line in enumerate(lines):
        if line.strip().startswith('def '):
            func_line_idx = i
            break
    
    if func_line_idx == -1:
        return function_def
    
    # Build the new parameter
    new_param = f'permission_check: bool = Depends(require_permission("{permission_code}"))'
    
    # Find the function parameters
    func_start = func_line_idx
    func_end = func_line_idx
    
    # Find where parameters end
    for i in range(func_start, len(lines)):
        if ')' in lines[i] and ':' in lines[i]:
            func_end = i
            break
    
    # Modify the function signature
    func_line = lines[func_line_idx]
    param_section = '\n'.join(lines[func_start:func_end+1])
    
    # Add new parameter before the closing )
    if ') -> Any:' in param_section or ') -> ' in param_section:
        param_section = param_section.replace(
            ')',
            f',\n    {new_param}\n    )',
            1
        )
    else:
        # No return type hint
        param_section = param_section.replace(
            ')',
            f',\n    {new_param}\n    )',
            1
        )
    
    # Rebuild function definition
    result = '\n'.join(lines[:func_start]) + '\n' + param_section + '\n' + '\n'.join(lines[func_end+1:])
    
    return result


print("\n" + "="*80)
print("FASE 5: Protezione degli Endpoint con Permission Checking")
print("="*80 + "\n")

endpoints_dir = get_endpoints_dir()
print(f"📁 Directory endpoints: {endpoints_dir}\n")

if not endpoints_dir.exists():
    print(f"❌ Directory non trovata: {endpoints_dir}")
    exit(1)

# Process each endpoint file
for file_name, protections in ENDPOINT_PROTECTIONS.items():
    file_path = endpoints_dir / file_name
    
    if not file_path.exists():
        print(f"⚠️  {file_name}: File non trovato (skipped)")
        continue
    
    print(f"ℹ️  {file_name}: Lettura...")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Add imports if needed
    content = add_permission_import(content)
    
    print(f"   ✓ Import aggiunti")
    
    # If content changed, save it
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)

print("\n✅ Script di protezione completato!")
print("⚠️  NOTA: Le protezioni devono essere applicate manualmente a ogni endpoint")
print("    per evitare errori di parsing. Guarda i dettagli in FASE_5_PROTEZIONI.md\n")
