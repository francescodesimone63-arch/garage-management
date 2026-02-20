"""
Work order models for managing repair jobs

BUSINESS RULE - APPROVAZIONE OBBLIGATORIA:
Tutte le schede lavoro richiedono approvazione del Garage Manager (GM).
Non esistono approvazioni automatiche, indipendentemente da:
- Importo dell'intervento
- Tipo di cliente (nuovo o fidelizzato)
- Tipologia di lavoro
- Richiesta auto cortesia

Stati del workflow:
- BOZZA: Stato iniziale, in attesa di approvazione GM
- APPROVATA: Approvata dal GM, pronta per pianificazione
- IN_LAVORAZIONE: Lavori in corso
- COMPLETATA: Lavori terminati
- ANNULLATA: Scheda annullata
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, DECIMAL, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class WorkOrderStatus(str, enum.Enum):
    """Work order status enumeration"""
    BOZZA = "bozza"
    APPROVATA = "approvata"
    IN_LAVORAZIONE = "in lavorazione"
    COMPLETATA = "completata"
    ANNULLATA = "annullata"


class Priority(str, enum.Enum):
    """Priority level enumeration"""
    BASSA = "bassa"
    MEDIA = "media"
    ALTA = "alta"
    URGENTE = "urgente"


class ActivityType(str, enum.Enum):
    """Activity type enumeration"""
    MECCANICA = "meccanica"
    CARROZZERIA = "carrozzeria"


class ActivityStatus(str, enum.Enum):
    """Activity status enumeration"""
    DA_FARE = "da_fare"
    IN_CORSO = "in_corso"
    COMPLETATA = "completata"


class PartStatus(str, enum.Enum):
    """Part status enumeration"""
    DA_ORDINARE = "da_ordinare"
    IN_ARRIVO = "in_arrivo"
    DISPONIBILE = "disponibile"
    UTILIZZATA = "utilizzata"
    NON_UTILIZZATA = "non_utilizzata"


class WorkOrder(Base):
    """Work order model"""
    __tablename__ = "work_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_scheda = Column(String(20), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    data_creazione = Column(DateTime(timezone=True), server_default=func.now())
    data_compilazione = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    data_appuntamento = Column(DateTime(timezone=True), index=True)
    data_fine_prevista = Column(DateTime(timezone=True))
    data_completamento = Column(DateTime(timezone=True))
    stato = Column(Enum(WorkOrderStatus), default=WorkOrderStatus.BOZZA, index=True)
    priorita = Column(Enum(Priority), default=Priority.MEDIA)
    valutazione_danno = Column(Text)
    sinistro = Column(Boolean, default=False, index=True)
    ramo_sinistro_id = Column(Integer, ForeignKey("insurance_branch_types.id"), nullable=True)
    legale = Column(Text, nullable=True)
    autorita = Column(Text, nullable=True)
    numero_sinistro = Column(String(50), nullable=True)
    compagnia_sinistro = Column(String(200), nullable=True)
    compagnia_debitrice_sinistro = Column(String(200), nullable=True)
    scoperto = Column(DECIMAL(10, 2), nullable=True)
    perc_franchigia = Column(DECIMAL(5, 2), nullable=True)
    creato_da = Column(Integer, ForeignKey("users.id"))
    approvato_da = Column(Integer, ForeignKey("users.id"))
    auto_cortesia_id = Column(Integer, ForeignKey("courtesy_cars.id"))
    costo_stimato = Column(DECIMAL(10, 2))
    costo_finale = Column(DECIMAL(10, 2))
    google_event_id = Column(String(255), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="work_orders")
    vehicle = relationship("Vehicle", back_populates="work_orders")
    creator = relationship("User", foreign_keys=[creato_da])
    approver = relationship("User", foreign_keys=[approvato_da])
    courtesy_car = relationship("CourtesyCar")
    insurance_branch = relationship("InsuranceBranchType")
    interventions = relationship("Intervention", back_populates="work_order", cascade="all, delete-orphan")
    activities = relationship("WorkOrderActivity", back_populates="work_order", cascade="all, delete-orphan")
    parts = relationship("WorkOrderPart", back_populates="work_order", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="work_order")
    calendar_event = relationship("CalendarEvent", back_populates="work_order", uselist=False, cascade="all, delete-orphan")
    car_assignment = relationship("CarAssignment", back_populates="work_order", uselist=False)
    
    def __repr__(self):
        return f"<WorkOrder(numero_scheda='{self.numero_scheda}', stato='{self.stato}')>"


class WorkOrderActivity(Base):
    """Work order activity model"""
    __tablename__ = "work_order_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    work_order_id = Column(Integer, ForeignKey("work_orders.id", ondelete="CASCADE"), nullable=False)
    descrizione = Column(Text, nullable=False)
    tipo = Column(Enum(ActivityType), nullable=False, index=True)
    assegnato_a = Column(String(10))  # CMM or CBM
    stato = Column(Enum(ActivityStatus), default=ActivityStatus.DA_FARE, index=True)
    ore_stimate = Column(DECIMAL(5, 2))
    ore_effettive = Column(DECIMAL(5, 2))
    costo_manodopera = Column(DECIMAL(10, 2))
    note = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    work_order = relationship("WorkOrder", back_populates="activities")
    
    def __repr__(self):
        return f"<WorkOrderActivity(tipo='{self.tipo}', stato='{self.stato}')>"


class WorkOrderPart(Base):
    """Work order parts model"""
    __tablename__ = "work_order_parts"
    
    id = Column(Integer, primary_key=True, index=True)
    work_order_id = Column(Integer, ForeignKey("work_orders.id", ondelete="CASCADE"), nullable=False)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False)
    quantita_richiesta = Column(DECIMAL(10, 2), nullable=False)
    quantita_utilizzata = Column(DECIMAL(10, 2), default=0)
    stato = Column(Enum(PartStatus), default=PartStatus.DA_ORDINARE, index=True)
    data_ordine = Column(DateTime(timezone=True))
    data_arrivo = Column(DateTime(timezone=True))
    data_utilizzo = Column(DateTime(timezone=True))
    fornitore_ordine = Column(String(200))
    prezzo_acquisto = Column(DECIMAL(10, 2))
    note = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    work_order = relationship("WorkOrder", back_populates="parts")
    part = relationship("Part")
    
    def __repr__(self):
        return f"<WorkOrderPart(part_id={self.part_id}, stato='{self.stato}')>"