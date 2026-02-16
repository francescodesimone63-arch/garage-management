# 5 Proposte di Layout Compatti per la Lista Schede Lavoro

> 🎯 Attualmente i caratteri/righe della lista sono troppo grandi  
> 💡 Ecco 5 proposte di layout compatti con diversi stili

---

## **PROPOSTA 1: Layout Minimalista Orizzontale (Compact Horizontal)**

```
┌─────────────────────────────────────────────────────────────────┐
│ TEST-6289  │ De Simone │ BMW X3 EW800ND │ 12/02 → 13/02 │ Bozza │
│ Compilata: 11/02      · Stimato: €100.000                       │
└─────────────────────────────────────────────────────────────────┘
```

**Caratteristiche:**
- Riga principale: Numero, Cliente, Veicolo, Date, Stato (tutto in una riga)
- Riga secondaria: Data compilazione + Costo stimato
- Altezza: ~50px per entry
- Colore stato come badge piccolo
- Migliore per: Monitor larghi, molti dati visibili contemporaneamente

---

## **PROPOSTA 2: Layout Card Compatto (Compact Card)**

```
┌────────────────────────────────────────────┐
│ TEST-6289 🟦 Bozza                         │
│ De Simone · BMW X3 (EW800ND)              │
│ 📅 Comp: 11/02  Appt: 12/02  Cons: 13/02 │
│ 💰 €100.000 · ⚙️ Meccanica                │
└────────────────────────────────────────────┘
```

**Caratteristiche:**
- 4 righe compatte per entry
- Numero + badge stato in header
- Cliente + Veicolo in una riga
- Date compresse con icone
- Costo + Tipo danno in footer
- Altezza: ~70px per card
- Migliore per: Tablet, lettura veloce con icone

---

## **PROPOSTA 3: Layout Tabella Ristrutturata (Restructured Table)**

```
┌──────────┬────────────┬──────────┬──────────┬────────┐
│ Scheda   │ Cliente    │ Data     │ Stato    │ Costo  │
│ TEST-622 │ De Simone  │ 11/02    │ 🟦 Bozza │ €100K  │
│ 9*       │            │          │          │        │
│          │ BMW X3     │ 12/02→   │          │ Mec.   │
│          │ EW800ND    │ 13/02    │          │        │
└──────────┴────────────┴──────────┴──────────┴────────┘
```

**Caratteristiche:**
- Colonne primarie ridotte: Scheda, Cliente, Data, Stato, Costo
- Espandersi per vedere dettagli (veicolo, date consegna, tipo danno)
- Font: 12px
- Altezza: ~40px riga normale, expandibile
- Migliore per: Desktop con schermi standard

---

## **PROPOSTA 4: Layout Timeline Compatto (Timeline)**

```
11/02  TEST-6289  Bozza
       De Simone (BMW X3)
       €100.000
       
12/02  TEST-6288  Approvata ──→ [Vedi Dettagli]
       Paolo Rossi (Fiat 500)
       €50.000
```

**Caratteristiche:**
- Asse temporale verticale per sequenza della settimana
- Data compilazione come anchor
- Informazioni compatte per riga
- Badge colore stato
- Migliore per: Mobile-first, view settimanale

---

## **PROPOSTA 5: Layout Ribbon Compatto (Ribbon/Strip)**

```
╔════════════════════════════════════════╗
║ TEST-6289 | 11/02 | 🟦 Bozza | €100K  ║
║ De Simone | BMW X3 (EW800ND)          ║
╚════════════════════════════════════════╝

╔════════════════════════════════════════╗
║ TEST-6288 | 11/02 | 🟧 Appr. | €50K   ║
║ Paolo Rossi | Fiat 500 (AB123CD)      ║
╚════════════════════════════════════════╝
```

**Caratteristiche:**
- 2 righe per entry
- Riga 1: Numero + Data + Stato + Costo (tutta inline)
- Riga 2: Cliente + Veicolo (più piccolo)
- Altezza: ~45px per entry
- Separazione visiva con bordo
- Migliore per: Lettura veloce, focus sui dati essenziali

---

## **Confronto Visivo Riassuntivo**

| Proposta  | Altezza | Colonne | Readability | Mobile | Multi-info |
|----------|---------|---------|------------|--------|-----------|
| 1: Orizzontale    | 50px | 5 | ⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ |
| 2: Card           | 70px | 3-4 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| 3: Tabella Risp.  | 40px | 4+exp | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| 4: Timeline       | 60px | Verticale | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| 5: Ribbon         | 45px | 2 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## **Raccomandazioni**

### Scegli se:

- **Proposta 1** → Vuoi massimizzare info in una sola riga, hai monitor larghi
- **Proposta 2** → Vuoi un look moderno con icone, supporto mobile buono
- **Proposta 3** → Preferisci il layout tabella tradizionale ma compatto
- **Proposta 4** → Vuoi enfasi sulla timeline/sequenza temporale
- **Proposta 5** → Vuoi equilibrio tra compattezza e leggibilità

---

## **Implementazione Tecnica (Ant Design)**

### Proposta 1 - Una riga compatta:
```tsx
// Usare Table con size="small", elimina padding eccesso
<Table size="small" pagination={{ pageSize: 20 }} />
// Colonne: numero, cliente, veicolo, date (formattate), stato
```

### Proposta 2 - Card compatta:
```tsx
// Usare List con renderItem personalizzato
// Ogni item è un Card con 4 righe di testo
<List renderItem={(wo) => <Card style={{height: '70px'}}></Card>} />
```

### Proposta 3 - Tabella expandibile:
```tsx
// Table con expandedRowRender per dettagli
<Table expandable={{ expandedRowRender: (record) => <Details /> }} />
```

### Proposta 4 - Timeline:
```tsx
// Usare Timeline di Ant Design
<Timeline items={groupedByDate} />
```

### Proposta 5 - Ribbon:
```tsx
// Custom component con Row + Border
// 2 Row per entry, Row principale con Space.Compact
```

---

## ✅ Prossimi Passi

Una volta scelta la proposta:  
1. ✏️ Scegli quale implementare (1-5)
2. 🎨 Comunica preferenze di colore/icone
3. 📊 Aggiungiamo le colonne/info che vuoi visualizzare
4. 🚀 Implementiamo il layout scelto
