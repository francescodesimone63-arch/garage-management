# 🎯 FIX COMPLETO WORK ORDER - ALLINEAMENTO BACKEND-FRONTEND

## 📋 PROBLEMA IDENTIFICATO

**Disallineamento totale** tra Schema Pydantic e Model SQLAlchemy nel backend, causando fallimento delle creazioni di schede lavoro.

### Root Cause
Il file `backend/app/schemas/work_order.py` usava nomi di campi diversi rispetto al `backend/app/models/work_order.py` (database).

## ✅ SOLUZIONE IMPLEMENTATA

### 1. **Backend Schema Corretto** (`backend/app/schemas/work_order.py`)

#### WorkOrderBase - PRIMA (ERRATO):
```python
data_ingresso: datetime
data_prevista_consegna: Optional[datetime]
km_ingresso: Optional[int]
descrizione_lavori: str
note_interne: Optional[str]
preventivo_importo: Optional[float]
numero_ordine: str
```

#### WorkOrderBase - DOPO (CORRETTO):
```python
numero_scheda: str  # ← REQUIRED!
data_appuntamento: datetime
data_fine_prevista: Optional[datetime]
data_completamento: Optional[datetime]
tipo_danno: Optional[str]
priorita: Optional[str]
valutazione_danno: str  # ← REQUIRED!
note: Optional[str]
costo_stimato: Optional[float]
costo_finale: Optional[float]
creato_da: Optional[int]
approvato_da: Optional[int]
auto_cortesia_id: Optional[int]
```

#### WorkOrderUpdate - Anche corretto con gli stessi nomi

---

### 2. **Frontend Types Corretti** (`frontend/src/types/index.ts`)

#### WorkOrderStatus - PRIMA (ERRATO):
```typescript
NUOVO = 'nuovo'
IN_ATTESA = 'in_attesa'
SOSPESO = 'sospeso'
COMPLETATO = 'completato'
CONSEGNATO = 'consegnato'
ANNULLATO = 'annullato'
```

#### WorkOrderStatus - DOPO (CORRETTO):
```typescript
BOZZA = 'bozza'
APPROVATA = 'approvata'
IN_LAVORAZIONE = 'in_lavorazione'
COMPLETATA = 'completata'
ANNULLATA = 'annullata'
```

#### WorkOrder Interface - PRIMA (ERRATO):
```typescript
numero_ordine: string
data_ingresso: string
data_prevista_consegna?: string
km_ingresso?: number
descrizione_lavori: string
note_interne?: string
preventivo_importo?: number
```

#### WorkOrder Interface - DOPO (CORRETTO):
```typescript
numero_scheda: string  // ← ALLINEATO!
data_appuntamento: string
data_fine_prevista?: string
data_completamento?: string
tipo_danno?: string
priorita?: string
valutazione_danno: string  // ← ALLINEATO!
note?: string
costo_stimato?: number
costo_finale?: number
creato_da?: number
approvato_da?: number
auto_cortesia_id?: number
```

---

### 3. **Frontend Form Corretto** (`frontend/src/pages/work-orders/WorkOrdersPage.tsx`)

#### Campi Form Aggiunti/Corretti:
```tsx
<Form.Item name="numero_scheda" label="Numero Scheda" rules={[{ required: true }]}>
  <Input placeholder="SL-2026-001" maxLength={20} />
</Form.Item>

<Form.Item name="priorita" label="Priorità" initialValue="media">
  <Select>
    <Select.Option value="bassa">Bassa</Select.Option>
    <Select.Option value="media">Media</Select.Option>
    <Select.Option value="alta">Alta</Select.Option>
    <Select.Option value="urgente">Urgente</Select.Option>
  </Select>
</Form.Item>

<Form.Item name="tipo_danno" label="Tipo Danno">
  <Select allowClear>
    <Select.Option value="meccanica">Meccanica</Select.Option>
    <Select.Option value="carrozzeria">Carrozzeria</Select.Option>
    <Select.Option value="elettronica">Elettronica</Select.Option>
    <Select.Option value="altro">Altro</Select.Option>
  </Select>
</Form.Item>

<Form.Item name="data_appuntamento" label="Data Appuntamento" rules={[{ required: true }]}>
  <Input type="date" />
</Form.Item>

<Form.Item name="data_fine_prevista" label="Consegna Prevista">
  <Input type="date" />
</Form.Item>

<Form.Item name="costo_stimato" label="Costo Stimato (€)">
  <InputNumber min={0} step={0.01} />
</Form.Item>

<Form.Item name="valutazione_danno" label="Descrizione Lavori" rules={[{ required: true }]}>
  <Input.TextArea rows={4} />
</Form.Item>

<Form.Item name="note" label="Note">
  <Input.TextArea rows={2} />
</Form.Item>
```

#### Stati Corretti:
```tsx
const statuses = [
  { value: 'bozza', label: 'Bozza', color: 'cyan' },
  { value: 'approvata', label: 'Approvata', color: 'orange' },
  { value: 'in_lavorazione', label: 'In Lavorazione', color: 'blue' },
  { value: 'completata', label: 'Completata', color: 'green' },
  { value: 'annullata', label: 'Annullata', color: 'default' },
]
```

#### Tabella Columns Corretti:
```tsx
{
  title: 'N° Scheda',
  dataIndex: 'numero_scheda',  // ← era numero_ordine
}
{
  title: 'Data Appuntamento',
  dataIndex: 'data_appuntamento',  // ← era data_ingresso
}
{
  title: 'Consegna Prevista',
  dataIndex: 'data_fine_prevista',  // ← era data_prevista_consegna
}
```

#### handleEdit Corretto:
```tsx
const handleEdit = (record: WorkOrder) => {
  setEditingWorkOrder(record)
  setSelectedCustomerId(record.customer_id)
  form.setFieldsValue({
    ...record,
    data_appuntamento: record.data_appuntamento ? dayjs(record.data_appuntamento).format('YYYY-MM-DD') : undefined,
    data_fine_prevista: record.data_fine_prevista ? dayjs(record.data_fine_prevista).format('YYYY-MM-DD') : undefined,
  })
  setIsModalOpen(true)
}
```

---

## 📊 MAPPATURA COMPLETA CAMPI

| **Model DB** | **Schema Backend** | **Frontend Form** | **TypeScript** | **Status** |
|--------------|-------------------|------------------|----------------|------------|
| numero_scheda | numero_scheda | numero_scheda | numero_scheda | ✅ ALLINEATO |
| data_appuntamento | data_appuntamento | data_appuntamento | data_appuntamento | ✅ ALLINEATO |
| data_fine_prevista | data_fine_prevista | data_fine_prevista | data_fine_prevista | ✅ ALLINEATO |
| data_completamento | data_completamento | - | data_completamento | ✅ ALLINEATO |
| tipo_danno | tipo_danno | tipo_danno | tipo_danno | ✅ ALLINEATO |
| priorita | priorita | priorita | priorita | ✅ ALLINEATO |
| valutazione_danno | valutazione_danno | valutazione_danno | valutazione_danno | ✅ ALLINEATO |
| note | note | note | note | ✅ ALLINEATO |
| costo_stimato | costo_stimato | costo_stimato | costo_stimato | ✅ ALLINEATO |
| costo_finale | costo_finale | - | costo_finale | ✅ ALLINEATO |
| stato | stato | stato | stato | ✅ ALLINEATO |
| creato_da | creato_da | - | creato_da | ✅ ALLINEATO |
| approvato_da | approvato_da | - | approvato_da | ✅ ALLINEATO |
| auto_cortesia_id | auto_cortesia_id | - | auto_cortesia_id | ✅ ALLINEATO |

---

## 🎯 STATI WORK ORDER CORRETTI

### Backend (Model):
```python
class WorkOrderStatus(str, enum.Enum):
    BOZZA = "bozza"
    APPROVATA = "approvata"
    IN_LAVORAZIONE = "in_lavorazione"
    COMPLETATA = "completata"
    ANNULLATA = "annullata"
```

### Frontend (TypeScript):
```typescript
export enum WorkOrderStatus {
  BOZZA = 'bozza',
  APPROVATA = 'approvata',
  IN_LAVORAZIONE = 'in_lavorazione',
  COMPLETATA = 'completata',
  ANNULLATA = 'annullata',
}
```

**✅ 100% ALLINEATI!**

---

## 📝 FILES MODIFICATI

1. ✅ `backend/app/schemas/work_order.py` - WorkOrderBase e WorkOrderUpdate corretti
2. ✅ `frontend/src/types/index.ts` - WorkOrder interface e WorkOrderStatus enum corretti
3. ✅ `frontend/src/pages/work-orders/WorkOrdersPage.tsx` - Form, stati, tabella, handleEdit corretti

---

## ✅ VERIFICA FINALE

### Campi Required per Creazione:
- ✅ `vehicle_id` (int)
- ✅ `customer_id` (int)
- ✅ `numero_scheda` (string, max 20 caratteri)
- ✅ `data_appuntamento` (datetime)
- ✅ `valutazione_danno` (string - descrizione lavori)
- ✅ `stato` (default: 'bozza')

### Campi Opzionali:
- ✅ `data_fine_prevista`
- ✅ `data_completamento`
- ✅ `tipo_danno`
- ✅ `priorita` (default: 'media')
- ✅ `note`
- ✅ `costo_stimato`
- ✅ `costo_finale`
- ✅ `creato_da`
- ✅ `approvato_da`
- ✅ `auto_cortesia_id`

---

## 🚀 WORKFLOW COMPLETO FUNZIONANTE

1. ✅ Login
2. ✅ Creazione Cliente (con quick-add dal form work order)
3. ✅ Creazione Veicolo (con quick-add dal form work order)
4. ✅ **Creazione Scheda Lavoro** → **FUNZIONA!**
5. ✅ Visualizzazione lista schede
6. ✅ Modifica scheda
7. ✅ Eliminazione scheda

---

## 💡 LEZIONE APPRESA

**SEMPRE verificare che:**
1. Model SQLAlchemy (database) = fonte di verità
2. Schema Pydantic = deve rispecchiare esattamente il Model
3. TypeScript types = deve rispecchiare esattamente lo Schema
4. Form frontend = deve usare esattamente i nomi dei types

**Il problema era:** Schema Pydantic usava nomi diversi dal Model, causando errori di creazione perché FastAPI passava i dati dello schema al model con nomi incompatibili.

---

**Data Fix:** 11/02/2026  
**Status:** ✅ COMPLETATO E TESTATO  
**Risultato:** Sistema 100% funzionante
