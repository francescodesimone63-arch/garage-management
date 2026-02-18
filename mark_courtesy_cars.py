#!/usr/bin/env python3
"""
Script per marcare alcuni veicoli come auto di cortesia
"""
import requests
import time

BASE_URL = "http://localhost:8000"
# Token di default per admin
AUTH_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzM5ODc0Njc3LCJleHAiOjE3Mzk5NjEwNzd9.u3k-Z6kYJjv6L50JL-ZtTcZvK_Ll5p7yMzXG5mT-uq4"

def mark_vehicles_as_courtesy():
    """Marca i primi 3 veicoli come auto di cortesia"""
    
    # Ottieni lista veicoli
    print("📋 Recupero lista veicoli...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/vehicles",
            headers={"Authorization": AUTH_TOKEN},
            params={"limit": 100}
        )
        response.raise_for_status()
        
        vehicles = response.json()
        items = vehicles.get("items", [])
        
        print(f"✅ Trovati {len(items)} veicoli")
        
        if not items:
            print("❌ Nessun veicolo trovato")
            return
        
        # Marca i primi 3 come auto di cortesia
        marked_count = 0
        for vehicle in items[:5]:  # Prendi i primi 5
            vehicle_id = vehicle.get("id")
            targa = vehicle.get("targa")
            
            # Aggiorna il veicolo
            update_response = requests.put(
                f"{BASE_URL}/api/v1/vehicles/{vehicle_id}",
                json={"courtesy_car": True, "disponibile": True},
                headers={"Authorization": AUTH_TOKEN}
            )
            
            if update_response.status_code == 200:
                marked_count += 1
                print(f"✅ {targa} contrassegnato come auto di cortesia")
            else:
                print(f"❌ Errore per {targa}: {update_response.status_code}")
        
        print(f"\n🎉 {marked_count} veicoli marcati come auto di cortesia")
        
    except Exception as e:
        print(f"❌ Errore: {e}")

if __name__ == "__main__":
    # Attendi che il backend sia online
    print("⏳ Attesa dell'avvio del backend...")
    for i in range(30):
        try:
            requests.get(f"{BASE_URL}/health", timeout=1)
            print("✅ Backend online")
            break
        except:
            time.sleep(1)
            if i == 29:
                print("❌ Backend non raggiungibile")
                exit(1)
    
    mark_vehicles_as_courtesy()
