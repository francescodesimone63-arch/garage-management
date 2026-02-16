# Setup PostgreSQL su macOS - Garage Management System

## Problema: PostgreSQL non in esecuzione

L'errore "connection to server on socket" indica che PostgreSQL non è avviato.

## Soluzione: Avviare PostgreSQL

### Opzione 1: Se PostgreSQL è installato tramite Homebrew

```bash
# Avvia PostgreSQL
brew services start postgresql@14
# oppure
brew services start postgresql@15
# oppure (versione generica)
brew services start postgresql

# Verifica che sia in esecuzione
brew services list
```

### Opzione 2: Se PostgreSQL è installato con Postgres.app

1. Apri l'applicazione **Postgres.app** dalla cartella Applicazioni
2. Clicca sul pulsante "Start" per avviare il server
3. Il server sarà disponibile su porta 5432

### Opzione 3: Avvio manuale

```bash
# Se installato da Homebrew
pg_ctl -D /usr/local/var/postgresql@14 start
# oppure
pg_ctl -D /opt/homebrew/var/postgresql@14 start
```

## Verifica Installazione PostgreSQL

```bash
# Verifica se PostgreSQL è installato
which psql

# Verifica versione
psql --version

# Prova connessione
psql postgres
```

## Se PostgreSQL NON è installato

### Installa PostgreSQL con Homebrew

```bash
# Installa Homebrew (se non già installato)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Installa PostgreSQL
brew install postgresql@14

# Avvia servizio
brew services start postgresql@14

# Crea utente (opzionale)
createuser -s postgres
```

### Oppure usa Postgres.app (più semplice)

1. Scarica da: https://postgresapp.com/
2. Installa l'applicazione
3. Avvia Postgres.app
4. Clicca "Initialize" per creare il cluster database

## Setup Database dopo aver avviato PostgreSQL

```bash
cd garage-management/backend

# 1. Crea il database
createdb garage_management

# 2. Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Installa dipendenze
pip install -r requirements.txt

# 4. Configura .env
cp .env.example .env
nano .env  # o usa il tuo editor preferito

# Modifica DATABASE_URL con:
# DATABASE_URL=postgresql://postgres@localhost:5432/garage_management
# (nota: nessuna password se usi l'utente di default)

# 5. Popola database
python3 scripts/seed_database.py

# 6. Avvia server
python3 main.py
```

## Alternative: Usa SQLite (Solo per test)

Se hai problemi con PostgreSQL, puoi temporaneamente usare SQLite:

1. Modifica `backend/.env`:
```env
DATABASE_URL=sqlite:///./garage_management.db
```

2. Installa dipendenza SQLite:
```bash
pip install aiosqlite
```

3. Avvia normalmente:
```bash
python3 scripts/seed_database.py
python3 main.py
```

**Nota**: SQLite è solo per sviluppo/test, usa PostgreSQL in produzione.

## Comandi Utili PostgreSQL

```bash
# Lista database
psql -l

# Connetti a database
psql garage_management

# Elimina database
dropdb garage_management

# Crea database
createdb garage_management

# Backup database
pg_dump garage_management > backup.sql

# Restore database
psql garage_management < backup.sql
```

## Verifica Setup Completo

```bash
# 1. Verifica PostgreSQL in esecuzione
brew services list | grep postgresql

# 2. Verifica connessione
psql -U postgres -h localhost -d postgres -c "SELECT version();"

# 3. Verifica database creato
psql -l | grep garage_management

# 4. Test applicazione
cd garage-management/backend
source venv/bin/activate
python3 main.py
```

Vai su: http://localhost:8000/api/docs

## Risoluzione Problemi Comuni

### Porta già in uso
```bash
# Trova processo sulla porta 5432
lsof -i :5432
# Termina processo
kill -9 <PID>
```

### Permessi negati
```bash
# Dai permessi utente corrente
createuser -s $(whoami)
```

### Database già esistente
```bash
# Elimina e ricrea
dropdb garage_management
createdb garage_management
```

## Problemi Installazione Dipendenze Python

### Errore: Failed building wheel for psycopg2-binary / pydantic-core

**Causa**: Python 3.13 è troppo recente, mancano dipendenze di sistema o Rust.

### Soluzione 1: Usa Python 3.11 o 3.12 (Raccomandato)

```bash
# Installa Python 3.11 o 3.12 con Homebrew
brew install python@3.11
# oppure
brew install python@3.12

# Rimuovi vecchio venv
cd garage-management/backend
rm -rf venv

# Crea nuovo venv con Python 3.11/3.12
python3.11 -m venv venv
# oppure
python3.12 -m venv venv

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Soluzione 2: Installa dipendenze di sistema

```bash
# Installa PostgreSQL client libraries
brew install postgresql

# Installa Rust (necessario per pydantic 2.x)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env

# Riprova installazione
cd garage-management/backend
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Soluzione 3: Usa versioni pre-compilate

```bash
cd garage-management/backend
source venv/bin/activate

# Installa wheel per build più veloce
pip install wheel

# Installa psycopg2 invece di psycopg2-binary
pip install psycopg2

# Installa altre dipendenze
pip install -r requirements.txt
```

### Soluzione 4: Installazione con cache disabilitata

```bash
cd garage-management/backend
source venv/bin/activate
pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt
```

## Supporto

Per ulteriori problemi, consulta:
- Documentazione PostgreSQL: https://www.postgresql.org/docs/
- Homebrew PostgreSQL: https://formulae.brew.sh/formula/postgresql
- Postgres.app: https://postgresapp.com/documentation/
- Python Compatibility: https://devguide.python.org/versions/
