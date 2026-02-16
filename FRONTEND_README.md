# Frontend - Garage Management System

## Tecnologie Utilizzate

- **React 18** - Libreria UI
- **TypeScript** - Type safety
- **Vite** - Build tool e dev server
- **React Router** - Routing
- **Ant Design** - UI Components
- **TanStack Query** - Data fetching e caching
- **Axios** - HTTP client
- **Day.js** - Date manipulation

## Struttura del Progetto

```
frontend/
├── src/
│   ├── api/              # API client functions
│   ├── components/       # Componenti riutilizzabili
│   ├── contexts/         # React Contexts (Auth, Theme, etc.)
│   ├── hooks/            # Custom React Hooks
│   ├── layouts/          # Layout components
│   ├── lib/              # Configurazioni librerie (axios, etc.)
│   ├── pages/            # Pagine dell'applicazione
│   │   ├── auth/         # Login, Register
│   │   ├── dashboard/    # Dashboard
│   │   ├── customers/    # Gestione clienti
│   │   ├── vehicles/     # Gestione veicoli
│   │   ├── work-orders/  # Ordini di lavoro
│   │   ├── parts/        # Gestione ricambi
│   │   ├── tires/        # Gestione pneumatici
│   │   ├── courtesy-cars/# Auto cortesia
│   │   ├── maintenance/  # Manutenzioni
│   │   ├── calendar/     # Calendario
│   │   ├── notifications/# Notifiche
│   │   ├── users/        # Gestione utenti
│   │   └── profile/      # Profilo utente
│   ├── types/            # TypeScript types e interfaces
│   ├── utils/            # Funzioni utility
│   ├── config/           # Configurazioni
│   ├── App.tsx           # Root component
│   ├── main.tsx          # Entry point
│   └── index.css         # Global styles
├── public/               # Static assets
├── .env.example          # Environment variables template
├── .env                  # Environment variables (git ignored)
├── package.json          # Dependencies
├── tsconfig.json         # TypeScript config
├── vite.config.ts        # Vite config
└── index.html            # HTML template
```

## Setup

### Prerequisiti

- Node.js 18+ 
- npm 9+

### Installazione

```bash
# Installa le dipendenze
npm install

# Crea file .env
cp .env.example .env

# Modifica .env con le tue configurazioni
nano .env
```

### Variabili d'Ambiente

```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_APP_NAME=Garage Management System
VITE_APP_VERSION=1.0.0
```

## Sviluppo

```bash
# Avvia il development server
npm run dev

# Build per produzione
npm run build

# Preview build di produzione
npm run preview

# Lint del codice
npm run lint
```

## Architettura

### Autenticazione

L'autenticazione è gestita tramite:
- **AuthContext**: Mantiene lo stato dell'utente autenticato
- **JWT Token**: Salvato in localStorage
- **Axios Interceptor**: Aggiunge automaticamente il token alle richieste
- **PrivateRoute**: Protegge le route che richiedono autenticazione

### State Management

- **TanStack Query** per lo state del server (API data)
- **React Context** per lo state globale (auth, theme)
- **Local State** per UI state locale

### Routing

```
/ → redirect to /dashboard
/login → LoginPage
/dashboard → DashboardPage (protected)
/customers → CustomersPage (protected)
/vehicles → VehiclesPage (protected)
/work-orders → WorkOrdersPage (protected)
/parts → PartsPage (protected)
/tires → TiresPage (protected)
/courtesy-cars → CourtesyCarsPage (protected)
/maintenance → MaintenanceSchedulesPage (protected)
/calendar → CalendarPage (protected)
/notifications → NotificationsPage (protected)
/users → UsersPage (protected, admin only)
/profile → ProfilePage (protected)
```

### Gestione Errori

- **Axios Interceptor** cattura errori HTTP e mostra messaggi utente
- **Error Boundaries** catturano errori React
- **Query Error Handling** gestito da TanStack Query

### Performance

- **Code Splitting** con React.lazy()
- **Query Caching** con TanStack Query
- **Memoization** dove appropriato
- **Lazy Loading** delle immagini

## Componenti Principali

### MainLayout
Layout principale con sidebar, header e content area. Menu dinamico basato sul ruolo utente.

### PrivateRoute
Componente wrapper che protegge le route richiedendo autenticazione.

### AuthContext
Context provider che gestisce stato auth, login e logout.

## Stili

- **Ant Design Theme**: Configurabile in `main.tsx`
- **CSS Modules** per stili component-scoped
- **Global Styles** in `index.css`

## API Integration

Tutte le chiamate API utilizzano:
- Axios instance configurato (`lib/axios.ts`)
- Base URL da env variable
- Automatic token injection
- Error handling centralizzato
- Request/Response interceptors

## Testing

```bash
# Unit tests
npm run test

# E2E tests
npm run test:e2e

# Coverage
npm run test:coverage
```

## Build e Deploy

### Development Build
```bash
npm run build:dev
```

### Production Build
```bash
npm run build
```

### Docker
```bash
docker build -t garage-frontend .
docker run -p 3000:80 garage-frontend
```

## Troubleshooting

### Port già in uso
```bash
# Cambia porta in vite.config.ts
server: {
  port: 5174
}
```

### Errori di build
```bash
# Pulisci node_modules e reinstalla
rm -rf node_modules package-lock.json
npm install
```

### Problemi con TypeScript
```bash
# Rigenera types
npm run type-check
```

## Prossimi Sviluppi

- [ ] Implementare tutte le pagine CRUD complete
- [ ] Aggiungere upload/download documenti
- [ ] Integrare sistema di notifiche real-time
- [ ] Aggiungere filtri avanzati e ricerca
- [ ] Implementare export/import dati
- [ ] Aggiungere grafici e statistiche avanzate
- [ ] Ottimizzazione mobile
- [ ] Dark mode
- [ ] Multilingua (i18n)
- [ ] PWA support

## Supporto

Per problemi o domande:
- Apri un issue su GitHub
- Consulta la documentazione API
- Verifica i log del browser console

## Licenza

Proprietario - Tutti i diritti riservati
