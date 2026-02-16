# 🚨 DISALLINEAMENTO WORK ORDER - FRONTEND vs BACKEND

## Campi Form Frontend → Modello Backend

| Form Frontend | Modello Backend | Status | Note |
|---------------|-----------------|--------|------|
| `numero_ordine` | `numero_scheda` | ❌ ERRATO | Nome diverso |
| `customer_id` | `customer_id` | ✅ OK | - |
| `vehicle_id` | `vehicle_id` | ✅ OK | - |
| `data_ingresso` | `data_appuntamento` | ❌ ERRATO | Nome diverso |
| `data_prevista_consegna` | `data_fine_prevista` | ❌ ERRATO | Nome diverso |
| `stato` | `stato` | ✅ OK | - |
| `km_ingresso` | **NON ESISTE** | ❌ MANCA | Campo mancante |
| `preventivo_importo` | `costo_stimato` | ❌ ERRATO | Nome diverso |
| `descrizione_lavori` | `valutazione_danno` | ❌ ERRATO | Nome diverso |
| `note_interne` | `note` | ❌ ERRATO | Nome diverso |

## Campi Modello Backend non usati

- `numero_scheda` - Generato automaticamente
- `data_creazione` - Auto-generato
- `data_completamento` - Compilato dopo
- `tipo_danno` - Non usato nel form
- `priorita` - Non usato nel form
- `creato_da` - Auto-assegnato
- `approvato_da` - Compilato dopo
- `auto_cortesia_id` - Non usato nel form
- `costo_finale` - Compilato dopo

## ✅ SOLUZIONE

Modificare il form frontend per usare i nomi corretti:

```typescript
// Frontend form fields CORRETTI:
{
  customer_id: number,
  vehicle_id: number,
  data_appuntamento: string,  // era data_ingresso
  data_fine_prevista: string,  // era data_prevista_consegna
  stato: string,
  costo_stimato: number,       // era preventivo_importo
  valutazione_danno: string,   // era descrizione_lavori
  note: string,                // era note_interne
  // km_ingresso - RIMUOVERE (non esiste nel backend)
}
```
