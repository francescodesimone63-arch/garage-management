# 📊 Come Usare lo Schema ER Grafico

## 3 Formati Disponibili

### 1️⃣ **HTML Interattivo** (Raccomandato)
📁 **File:** `SCHEMA_ER.html`

**Come usare:**
- Apri il file in un browser: `Finder → SCHEMA_ER.html → Doppio click`
- O drag-drop nel browser
- O: `open SCHEMA_ER.html`

**Funzionalità:**
- ✅ Visualizza il diagramma interattivo
- ✅ Pulsante "Scarica come SVG" (vettoriale, scalabile)
- ✅ Pulsante "Scarica Markdown" (.md con Mermaid)
- ✅ Copia markup nel clipboard
- ✅ Bellissimo stile grafico

**Vantaggi:**
- Non richiede software aggiuntivo
- Visualizzazione immediata
- Esporti facili in un click

---

### 2️⃣ **Mermaid Puro** (.mmd)
📁 **File:** `SCHEMA_ER.mmd`

**Come usare:**

#### Opzione A: Editor Online (Gratuito)
1. Vai su: https://mermaid.live
2. Coppa-incolla contenuto di `SCHEMA_ER.mmd`
3. Clicca "Download as PNG/SVG"

#### Opzione B: VS Code
1. Installa estensione "Markdown Preview Mermaid Support"
2. Apri `SCHEMA_ER.mmd` in VS Code
3. Preview con Cmd+K, V (o click Preview)
4. Click destro → Salva come PNG

#### Opzione C: Terminale macOS
```bash
# Se haiBrew + Mermaid CLI:
brew install mermaid-cli
mmdc -i SCHEMA_ER.mmd -o SCHEMA_ER.png
```

**Output:**
- PNG a qualità alta
- SVG vettoriale scalabile

---

### 3️⃣ **Markdown con Diagram**
📁 **File:** `SCHEMA_ER_GARAGE_DB.md` (già contiene il diagramma)

**Come usare:**
- Apri in qualsiasi editor Markdown
- GitHub renderizza automaticamente il diagramma Mermaid
- Copia/incolla in Notion, Confluence, etc.

**Vantaggi:**
- Perfetto per documentazione
- Sincronizzazione con git
- Versioning automatico

---

## 🎯 Raccomandazioni Rapide

| Situazione | Soluzione | File |
|-----------|----------|------|
| Voglio vederlo subito | Apri `SCHEMA_ER.html` nel browser | `.html` |
| Voglio esportare PNG/SVG | Usa `SCHEMA_ER.html` + download button | `.html` |
| Voglio modificare il diagramma | Apri `SCHEMA_ER.mmd` in https://mermaid.live | `.mmd` |
| Voglio aggiungerlo in documentazione | Usa contenuto di `SCHEMA_ER_GARAGE_DB.md` | `.md` |
| Voglio stampa/PDF | Apri `.html` → Cmd+P → Salva PDF | `.html` |
| Lavoro in VS Code | Installa estensione Mermaid + apri `.mmd` | `.mmd` |

---

## 🖨️ Come Stampare/Esportare

### ✅ PDF da Browser
1. Apri `SCHEMA_ER.html`
2. Premi `Cmd+P` (Mac) / `Ctrl+P` (Windows)
3. Seleziona "Salva come PDF"
4. ✅ Fatto!

### ✅ PNG da Mermaid Live
1. Apri https://mermaid.live
2. Incolla `SCHEMA_ER.mmd`
3. Click tre puntini → "Download as PNG"
4. ✅ PNG ad alta risoluzione

### ✅ SVG Vettoriale (Scalabile)
1. Usa `SCHEMA_ER.html`
2. Click "Scarica come SVG"
3. Apri in Illustrator, Figma, o qualsiasi grafico software
4. ✅ Scalabile senza perdita di qualità

---

## 💡 Pro Tips

**Mac:**
```bash
# Apri HTML direttamente
open SCHEMA_ER.html

# Se installi mermaid-cli:
npm install -g @mermaid-js/mermaid-cli
mmdc -i SCHEMA_ER.mmd -o SCHEMA_ER.png -w 1920 -H 1080
```

**Condivisione Facile:**
- Se copi il markup da `.mmd`
- Puoi incollarlo in GitLab, GitHub, Notion, etc.
- Renderizzano automaticamente il diagramma

**Modifica:**
- Vuoi aggiungere/togliere relazioni? Edit il file `.mmd`
- Salva
- Ricaricare il browser → vedi cambio automatico

---

## 📝 Chiara Interpretazione del Diagramma

```
CUSTOMERS ||--o{ VEHICLES : "possiede"
│          └─┬─┘ │      └─────────┘
│            │   │        Etichetta relazione
│       Uno a molti (un cliente ha molti veicoli)
└─ CUSTOMERS ha molti VEHICLES
```

Legend:
- `||` = Uno esattamente
- `o{` = Uno a molti (uno a destra, molti a sinistra)
- `}o` = Molti (da sinistra)
- `|` = Esattamente uno (da destra)

---

## 🎨 Customizzazione

Vuoi modificare il diagramma? Edita `SCHEMA_ER.mmd`:

```mermaid
# Aggiungi una nuova relazione:
NUOVO_ENTE ||--o{ VECTORE_ESISTENTE : "descrizione"

# Ricarica SCHEMA_ER.html automaticamente renderizza il nuovo
```

---

**Creato:** 20 febbraio 2026
**Per:** Garage Management System
**Formati:** HTML, Mermaid, Markdown PDF/PNG/SVG exportable
