"""
Auto/Veicoli API - Marche, Modelli e Verifica Targa

Endpoints per la ricerca di marche e modelli auto, 
e verifica dati veicolo da targa.
"""
import json
import os
import re
import random
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models import User

router = APIRouter(tags=["auto"])

# Cache in-memory per rate limiting (in produzione usare Redis)
_rate_limit_cache: Dict[str, List[datetime]] = {}
RATE_LIMIT_MAX = 10  # max richieste
RATE_LIMIT_WINDOW = 60  # secondi

# Cache per risultati verifica targa (simula Redis)
_targa_cache: Dict[str, Dict[str, Any]] = {}
CACHE_TTL_HOURS = 24


def load_auto_data() -> Dict[str, Any]:
    """Carica dati marche/modelli da file JSON"""
    # Percorso assoluto basato sulla directory app
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    data_path = os.path.join(base_dir, "data", "auto_marche_modelli.json")
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


def check_rate_limit(ip: str) -> bool:
    """Verifica rate limiting per IP (max 10/min)"""
    now = datetime.now()
    window_start = now - timedelta(seconds=RATE_LIMIT_WINDOW)
    
    if ip not in _rate_limit_cache:
        _rate_limit_cache[ip] = []
    
    # Rimuovi richieste vecchie
    _rate_limit_cache[ip] = [
        t for t in _rate_limit_cache[ip] 
        if t > window_start
    ]
    
    if len(_rate_limit_cache[ip]) >= RATE_LIMIT_MAX:
        return False
    
    _rate_limit_cache[ip].append(now)
    return True


# === Schemas ===

class TargaRequest(BaseModel):
    """Schema per richiesta verifica targa"""
    targa: str
    
    @field_validator('targa')
    @classmethod
    def validate_targa(cls, v: str) -> str:
        # Normalizza: rimuovi spazi e converti in maiuscolo
        v = v.strip().upper().replace(" ", "").replace("-", "")
        
        # Formato targhe italiane:
        # - Nuovo formato (1994+): AA000AA (2 lettere, 3 numeri, 2 lettere)
        # - Vecchio formato: MI A00000 (provincia + lettere + numeri)
        pattern_nuovo = r'^[A-Z]{2}[0-9]{3}[A-Z]{2}$'
        pattern_vecchio = r'^[A-Z]{2}[A-Z0-9]{1,7}$'
        
        if not (re.match(pattern_nuovo, v) or re.match(pattern_vecchio, v)):
            raise ValueError('Formato targa non valido. Usa formato: AA000AA')
        
        return v


class TargaResponse(BaseModel):
    """Schema risposta verifica targa"""
    targa: str
    marca: str
    modello: str
    anno: int
    cilindrata: Optional[str] = None
    kw: Optional[int] = None
    cv: Optional[int] = None
    porte: Optional[int] = None
    carburante: Optional[str] = None
    telaio: Optional[str] = None
    colore: Optional[str] = None
    prima_immatricolazione: Optional[str] = None
    fonte: str = "mock"  # "mock" o "api_esterna"


class MarcaModelli(BaseModel):
    """Schema per marca con lista modelli"""
    nome: str
    modelli: List[str]


class MarcheResponse(BaseModel):
    """Schema risposta lista marche"""
    marche: List[str]
    count: int


class ModelliResponse(BaseModel):
    """Schema risposta lista modelli"""
    marca: str
    modelli: List[str]
    count: int


class CarburantiResponse(BaseModel):
    """Schema risposta lista carburanti"""
    carburanti: List[str]


# === Mock Data per Verifica Targa ===

def genera_dati_mock_targa(targa: str) -> Dict[str, Any]:
    """
    Genera dati mock per una targa.
    In produzione, questo chiamerebbe un'API esterna come targhe.it
    """
    auto_data = load_auto_data()
    marche = auto_data["marche"]
    carburanti = auto_data["carburanti"]
    
    # Usa hash della targa per generare dati consistenti
    targa_hash = hash(targa)
    random.seed(targa_hash)
    
    # Seleziona marca random
    marca_data = random.choice(marche)
    marca = marca_data["nome"]
    modello = random.choice(marca_data["modelli"])
    
    # Genera anno basato sulle prime lettere della targa
    # (approssimazione: targhe più recenti = lettere più avanti nell'alfabeto)
    first_letter = ord(targa[0]) - ord('A')
    anno_base = 1994 + (first_letter * 32 // 26)  # 1994-2026
    anno = min(max(anno_base + random.randint(-2, 2), 1994), 2026)
    
    # Dati tecnici random ma plausibili
    cilindrate = ["999 cc", "1199 cc", "1248 cc", "1332 cc", "1461 cc", "1598 cc", "1968 cc", "2143 cc", "2998 cc"]
    cilindrata = random.choice(cilindrate)
    
    kw = random.randint(44, 220)
    cv = int(kw * 1.36)
    
    porte = random.choice([3, 5])
    carburante = random.choice(carburanti[:5])  # Esclude ibride plug-in
    
    colori = ["Bianco", "Nero", "Grigio", "Rosso", "Blu", "Argento", "Verde", "Marrone"]
    colore = random.choice(colori)
    
    # Telaio fittizio
    telaio = f"ZFA{random.randint(100, 999)}{random.randint(1000000, 9999999)}"
    
    # Data prima immatricolazione
    mese = random.randint(1, 12)
    prima_imm = f"{anno}-{mese:02d}-01"
    
    return {
        "targa": targa,
        "marca": marca,
        "modello": modello,
        "anno": anno,
        "cilindrata": cilindrata,
        "kw": kw,
        "cv": cv,
        "porte": porte,
        "carburante": carburante,
        "telaio": telaio,
        "colore": colore,
        "prima_immatricolazione": prima_imm,
        "fonte": "mock"
    }


# === Endpoints ===

@router.get("/marche", response_model=MarcheResponse)
def get_marche(
    current_user: User = Depends(get_current_user)
) -> MarcheResponse:
    """
    Ottiene la lista delle marche auto disponibili.
    
    Top 50 marche vendute in Italia (dati UNRAE 2024-2026).
    Ordinate alfabeticamente.
    """
    auto_data = load_auto_data()
    marche = sorted([m["nome"] for m in auto_data["marche"]])
    return MarcheResponse(marche=marche, count=len(marche))


@router.get("/modelli/{marca}", response_model=ModelliResponse)
def get_modelli_by_marca(
    marca: str,
    current_user: User = Depends(get_current_user)
) -> ModelliResponse:
    """
    Ottiene la lista dei modelli per una marca specifica.
    
    Args:
        marca: Nome della marca (case insensitive)
    
    Returns:
        Lista di modelli disponibili per la marca
    """
    auto_data = load_auto_data()
    marca_upper = marca.upper().strip()
    
    for m in auto_data["marche"]:
        if m["nome"].upper() == marca_upper:
            modelli = sorted(m["modelli"])
            return ModelliResponse(marca=m["nome"], modelli=modelli, count=len(modelli))
    
    # Marca custom: restituisce lista vuota, l'utente può inserire modello manualmente
    return ModelliResponse(marca=marca, modelli=[], count=0)


@router.get("/marche-modelli", response_model=List[MarcaModelli])
def get_marche_modelli(
    current_user: User = Depends(get_current_user)
) -> List[MarcaModelli]:
    """
    Ottiene la lista completa di marche con i loro modelli.
    
    Utile per popolare dropdown a cascata (marca → modelli).
    """
    auto_data = load_auto_data()
    result = [
        MarcaModelli(nome=m["nome"], modelli=sorted(m["modelli"]))
        for m in sorted(auto_data["marche"], key=lambda x: x["nome"])
    ]
    return result


@router.get("/carburanti", response_model=CarburantiResponse)
def get_carburanti(
    current_user: User = Depends(get_current_user)
) -> CarburantiResponse:
    """
    Ottiene la lista dei tipi di carburante/alimentazione.
    """
    auto_data = load_auto_data()
    return CarburantiResponse(carburanti=auto_data["carburanti"])


@router.post("/verifica-targa", response_model=TargaResponse)
def verifica_targa(
    request: Request,
    data: TargaRequest,
    current_user: User = Depends(get_current_user)
) -> TargaResponse:
    """
    Verifica i dati di un veicolo dalla targa.
    
    Restituisce marca, modello, anno e altri dati tecnici.
    
    **Rate Limiting**: Max 10 richieste al minuto per IP.
    
    **Cache**: I risultati sono cachati per 24 ore.
    
    **Nota**: Attualmente usa dati mock. In produzione integrare
    con API esterna (es. targhe.it, motorizzazione.it).
    """
    # Rate limiting
    client_ip = request.client.host if request.client else "unknown"
    if not check_rate_limit(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Troppe richieste. Riprova tra un minuto."
        )
    
    targa = data.targa
    
    # Check cache
    if targa in _targa_cache:
        cache_entry = _targa_cache[targa]
        cache_time = cache_entry.get("_cached_at")
        if cache_time and datetime.now() - cache_time < timedelta(hours=CACHE_TTL_HOURS):
            # Rimuovi metadati cache dalla risposta
            result = {k: v for k, v in cache_entry.items() if not k.startswith("_")}
            return TargaResponse(**result)
    
    # Genera dati (mock o API esterna)
    # TODO: In produzione, sostituire con chiamata API reale
    result = genera_dati_mock_targa(targa)
    
    # Salva in cache
    _targa_cache[targa] = {**result, "_cached_at": datetime.now()}
    
    return TargaResponse(**result)


@router.get("/cerca-modello", response_model=List[Dict[str, str]])
def cerca_modello(
    q: str,
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, str]]:
    """
    Cerca modelli auto per nome (autocomplete).
    
    Args:
        q: Query di ricerca (min 2 caratteri)
    
    Returns:
        Lista di {marca, modello} che matchano la query
    """
    if len(q) < 2:
        return []
    
    auto_data = load_auto_data()
    q_lower = q.lower()
    
    results = []
    for marca_data in auto_data["marche"]:
        marca = marca_data["nome"]
        for modello in marca_data["modelli"]:
            if q_lower in modello.lower() or q_lower in marca.lower():
                results.append({
                    "marca": marca,
                    "modello": modello
                })
                if len(results) >= 20:
                    break
        if len(results) >= 20:
            break
    
    return results
