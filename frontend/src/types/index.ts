// User types
export enum UserRole {
  ADMIN = 'ADMIN',
  GENERAL_MANAGER = 'GM',      // Garage Manager
  CMM = 'CMM',                  // Capo Meccanica
  CBM = 'CBM',                  // Capo Carrozzeria
  WORKSHOP = 'WORKSHOP',        // Legacy - deprecato
  BODYSHOP = 'BODYSHOP',        // Legacy - deprecato
}

export interface User {
  id: number
  email: string
  username: string
  nome: string
  cognome: string
  ruolo: UserRole
  attivo: boolean
  created_at: string
  updated_at?: string
}

export interface RichiestaLogin {
  username: string
  password: string
}

export interface RispostaLogin {
  access_token: string
  token_type: string
  expires_in: number
  user: User
}

// Export aliases for backward compatibility
export type LoginRequest = RichiestaLogin
export type LoginResponse = RispostaLogin

// Customer types
export interface Customer {
  id: number
  tipo: string // 'privato' | 'azienda'
  nome?: string
  cognome?: string
  ragione_sociale?: string
  codice_fiscale: string
  partita_iva?: string
  indirizzo?: string
  citta?: string
  cap?: string
  provincia?: string
  telefono?: string
  cellulare?: string
  email?: string
  note?: string
  attivo?: boolean
  created_at: string
  updated_at?: string
}

export interface CustomerCreate {
  tipo: string // 'privato' | 'azienda'
  nome?: string
  cognome?: string
  ragione_sociale?: string
  codice_fiscale: string
  partita_iva?: string
  indirizzo?: string
  citta?: string
  cap?: string
  provincia?: string
  telefono?: string
  cellulare?: string
  email?: string
  note?: string
}

// Vehicle types - ALLINEATO AL BACKEND MODEL
export interface Vehicle {
  id: number
  customer_id: number
  targa: string
  telaio?: string
  marca: string
  modello: string
  anno?: number
  colore?: string
  km_attuali?: number
  note?: string
  attivo?: boolean
  // Campi tecnici aggiuntivi
  cilindrata?: string
  kw?: number
  cv?: number
  porte?: number
  carburante?: string
  prima_immatricolazione?: string
  created_at: string
  updated_at?: string
  customer?: Customer
}

// Auto lookup types
export interface DatiTargaResponse {
  targa: string
  marca: string
  modello: string
  anno: number
  cilindrata: string
  kw: number
  cv: number
  porte: number
  carburante: string
  telaio: string
  colore: string
  prima_immatricolazione: string
  fonte: string
}

// Work Order types - ALLINEATO AL BACKEND
export enum WorkOrderStatus {
  BOZZA = 'bozza',
  APPROVATA = 'approvata',
  IN_LAVORAZIONE = 'in_lavorazione',
  COMPLETATA = 'completata',
  ANNULLATA = 'annullata',
}

export enum WorkOrderPriority {
  BASSA = 'bassa',
  MEDIA = 'media',
  ALTA = 'alta',
  URGENTE = 'urgente',
}

export interface WorkOrder {
  id: number
  vehicle_id: number
  customer_id: number
  numero_scheda: string
  stato: WorkOrderStatus
  data_creazione?: string
  data_compilazione: string
  data_appuntamento: string
  data_fine_prevista?: string
  data_completamento?: string
  priorita?: string
  valutazione_danno: string
  note?: string
  creato_da?: number
  approvato_da?: number
  auto_cortesia_id?: number
  costo_stimato?: number
  costo_finale?: number
  created_at: string
  updated_at?: string
  // Relazioni
  vehicle?: Vehicle
  customer?: Customer
  // Dati denormalizzati per visualizzazione lista
  customer_nome?: string
  customer_email?: string
  customer_telefono?: string
  vehicle_targa?: string
  vehicle_marca?: string
  vehicle_modello?: string
  vehicle_anno?: number
  vehicle_colore?: string
  interventions?: Intervention[]
}

// Intervention Status Type
export interface InterventionStatusType {
  id: number
  codice: string
  nome: string
  descrizione?: string
  richiede_nota: boolean
  attivo: boolean
  ordine: number
  created_at: string
  updated_at: string
}

// Intervention types
export interface Intervention {
  id?: number
  work_order_id?: number
  progressivo?: number
  descrizione_intervento: string
  durata_stimata: number
  tipo_intervento: 'Meccanico' | 'Carrozziere'
  // Nuovi campi per gestione stato CMM/CBM
  stato_intervento_id?: number
  stato_intervento?: InterventionStatusType
  note_intervento?: string
  note_sospensione?: string
  ore_effettive?: number
  data_inizio?: string
  data_fine?: string
  created_at?: string
  updated_at?: string
  _isNew?: boolean // Mark new interventions not yet saved
  _modified?: boolean // Mark modified interventions
}

export interface InterventionCreate {
  descrizione_intervento: string
  durata_stimata: number
  tipo_intervento: 'Meccanico' | 'Carrozziere'
  stato_intervento_id?: number
  note_intervento?: string
}

export interface InterventionUpdate extends InterventionCreate {
  work_order_id: number
  note_sospensione?: string
  ore_effettive?: number
}

export interface InterventionStatusUpdate {
  stato_intervento_id: number
  note_intervento?: string
  note_sospensione?: string
}

export interface InterventionCreate {
  descrizione_intervento: string
  durata_stimata: number
  tipo_intervento: 'Meccanico' | 'Carrozziere'
  stato_intervento_id?: number
  note_intervento?: string
}

// CMM Work Order Summary (for CMM role)
export interface CMMInterventionSummary {
  id: number
  progressivo: number
  descrizione_intervento: string
  durata_stimata: number
  tipo_intervento: 'Meccanico' | 'Carrozziere'
  stato_intervento_id?: number
  stato_intervento_codice?: string
  stato_intervento_nome?: string
  note_intervento?: string
  note_sospensione?: string
  ore_effettive?: number
  data_inizio?: string
  data_fine?: string
}

export interface CMMWorkOrderSummary {
  id: number
  numero_scheda: string
  stato: string
  data_appuntamento?: string
  data_fine_prevista?: string
  priorita?: string
  note?: string
  cliente_nome?: string
  cliente_cognome?: string
  cliente_telefono?: string
  veicolo_targa?: string
  veicolo_marca?: string
  veicolo_modello?: string
  interventi: CMMInterventionSummary[]
  ha_interventi_meccanica: boolean
}

// CMM Dashboard Stats
export interface InterventionStatusStats {
  codice: string
  nome: string
  totale: number
}

export interface CMMDashboardStats {
  work_orders_approvate: number
  work_orders_in_lavorazione: number
  customers_total: number
  vehicles_total: number
  interventi_totali: number
  interventi_senza_stato: number
  interventi_per_stato: InterventionStatusStats[]
}

// Part types - ALLINEATO AL BACKEND MODEL
export interface Part {
  id: number
  codice: string
  nome: string
  descrizione?: string
  categoria?: string
  marca?: string
  modello?: string
  quantita: number
  quantita_minima: number
  prezzo_acquisto?: number
  prezzo_vendita?: number
  fornitore?: string
  posizione_magazzino?: string
  tipo: string // 'ricambio' | 'fornitura'
  unita_misura?: string
  note?: string
  created_at: string
  updated_at?: string
}

// Tire types
export enum TirePosition {
  FRONT_LEFT = 'front_left',
  FRONT_RIGHT = 'front_right',
  REAR_LEFT = 'rear_left',
  REAR_RIGHT = 'rear_right',
}

export enum TireSeason {
  ESTIVO = 'estivo',
  INVERNALE = 'invernale',
}

export enum TireCondition {
  NUOVO = 'nuovo',
  BUONO = 'buono',
  DISCRETO = 'discreto',
  USATO = 'usato',
  CONSUNTO = 'consunto',
}

export enum TireStatus {
  DEPOSITATI = 'depositati',
  MONTATI = 'montati',
}

export interface Tire {
  id: number
  vehicle_id: number
  tipo_stagione: TireSeason
  marca?: string
  modello?: string
  misura?: string
  data_deposito?: string
  data_ultimo_cambio?: string
  data_prossimo_cambio?: string
  stato: TireStatus
  posizione?: TirePosition
  condizione: TireCondition
  profondita_battistrada?: number
  data_produzione?: string
  data_ultima_rotazione?: string
  km_ultima_rotazione?: number
  posizione_deposito?: string
  note?: string
  created_at: string
  updated_at?: string
  vehicle?: Vehicle
}

// Courtesy Car types - ALLINEATO AL BACKEND MODEL
export enum CourtesyCarStatus {
  DISPONIBILE = 'disponibile',
  ASSEGNATA = 'assegnata',
  MANUTENZIONE = 'manutenzione',
  FUORI_SERVIZIO = 'fuori_servizio',
}

export enum ContractType {
  LEASING = 'leasing',
  AFFITTO = 'affitto',
  PROPRIETA = 'proprieta',
}

export interface CourtesyCar {
  id: number
  vehicle_id: number
  contratto_tipo: ContractType
  fornitore_contratto?: string
  data_inizio_contratto?: string
  data_scadenza_contratto?: string
  canone_mensile?: number
  km_inclusi_anno?: number
  stato: CourtesyCarStatus
  note?: string
  created_at: string
  updated_at?: string
  vehicle?: Vehicle
}

export enum AssignmentStatus {
  PRENOTATA = 'prenotata',
  IN_CORSO = 'in_corso',
  COMPLETATA = 'completata',
  ANNULLATA = 'annullata',
}

export interface CarAssignment {
  id: number
  courtesy_car_id: number
  work_order_id?: number
  customer_id: number
  data_inizio: string
  data_fine_prevista: string
  data_fine_effettiva?: string
  km_inizio?: number
  km_fine?: number
  stato: AssignmentStatus
  note?: string
  created_at: string
  updated_at?: string
  courtesy_car?: CourtesyCar
  customer?: Customer
  work_order?: WorkOrder
}

// Maintenance Schedule types - ALLINEATO AL BACKEND MODEL
export enum MaintenanceType {
  ORDINARIA = 'ordinaria',
  STRAORDINARIA = 'straordinaria',
}

export enum MaintenanceStatus {
  ATTIVA = 'attiva',
  COMPLETATA = 'completata',
  ANNULLATA = 'annullata',
}

export interface MaintenanceSchedule {
  id: number
  vehicle_id: number
  tipo: MaintenanceType
  descrizione: string
  km_scadenza?: number
  data_scadenza?: string
  km_preavviso: number
  giorni_preavviso: number
  stato: MaintenanceStatus
  ricorrente: boolean
  intervallo_km?: number
  intervallo_giorni?: number
  ultima_notifica?: string
  note?: string
  created_at: string
  updated_at?: string
  vehicle?: Vehicle
}

// Notification types
export enum NotificationPriority {
  BASSA = 'bassa',
  NORMALE = 'normale',
  ALTA = 'alta',
  URGENTE = 'urgente',
}

export interface Notification {
  id: number
  user_id: number
  title: string
  message: string
  priority: NotificationPriority
  is_read: boolean
  related_entity_type?: string
  related_entity_id?: number
  action_url?: string
  created_at: string
  read_at?: string
  user?: User
}

// Calendar Event types
export enum EventType {
  APPUNTAMENTO = 'appuntamento',
  MANUTENZIONE = 'manutenzione',
  CONSEGNA = 'consegna',
  RIUNIONE = 'riunione',
  PROMEMORIA = 'promemoria',
  ALTRO = 'altro',
}

export interface CalendarEvent {
  id: number
  title: string
  description?: string
  event_type: EventType
  start_datetime: string
  end_datetime?: string
  all_day: boolean
  location?: string
  related_entity_type?: string
  related_entity_id?: number
  created_by_id: number
  assigned_to_id?: number
  reminder_before_minutes?: number
  is_recurring: boolean
  recurrence_rule?: string
  created_at: string
  updated_at?: string
  created_by?: User
  assigned_to?: User
}

// Activity Log types
export enum ActivityAction {
  CREA = 'crea',
  AGGIORNA = 'aggiorna',
  CANCELLA = 'cancella',
  VISUALIZZA = 'visualizza',
  ESPORTA = 'esporta',
  ACCESSO = 'accesso',
  USCITA = 'uscita',
  ALTRO = 'altro',
}

export interface ActivityLog {
  id: number
  user_id: number
  action: ActivityAction
  entity_type: string
  entity_id?: number
  description: string
  ip_address?: string
  user_agent?: string
  created_at: string
  user?: User
}

// Document types
export enum DocumentType {
  FATTURA = 'fattura',
  PREVENTIVO = 'preventivo',
  SCHEDA_LAVORO = 'scheda_lavoro',
  RICEVUTA = 'ricevuta',
  CONTRATTO = 'contratto',
  ASSICURAZIONE = 'assicurazione',
  ALTRO = 'altro',
}

export interface Document {
  id: number
  entity_type: string
  entity_id: number
  document_type: DocumentType
  file_name: string
  file_path: string
  file_size: number
  mime_type: string
  uploaded_by_id: number
  description?: string
  is_active: boolean
  created_at: string
  updated_at?: string
  uploaded_by?: User
}

// Dashboard types
export interface DashboardSummary {
  role: UserRole
  stats: {
    work_orders_open?: number
    work_orders_in_progress?: number
    work_orders_pending_approval?: number
    customers_total?: number
    vehicles_total?: number
    parts_low_stock?: number
    courtesy_cars_available?: number
    maintenance_alerts?: number
    unread_notifications?: number
  }
  recent_work_orders?: WorkOrder[]
  alerts?: any[]
}

// Pagination
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}
