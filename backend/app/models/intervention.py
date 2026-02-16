"""
Intervention (Intervento) model for work orders

Un intervento rappresenta un compito specifico all'interno di una scheda lavoro.
Ogni intervento ha:
- Un progressivo univoco all'interno della scheda
- Una descrizione
- Una durata stimata in ore (formato decimale)
- Un tipo (Meccanico o Carrozziere)
- Uno stato intervento (preso_in_carico, attesa_componente, sospeso, concluso)
- Note opzionali
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, DECIMAL, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Intervention(Base):
    """Intervention (Intervento) model"""
    __tablename__ = "interventions"
    
    id = Column(Integer, primary_key=True, index=True)
    work_order_id = Column(Integer, ForeignKey("work_orders.id", ondelete="CASCADE"), nullable=False)
    progressivo = Column(Integer, nullable=False)  # 1, 2, 3, ... per ogni scheda
    descrizione_intervento = Column(Text, nullable=False)
    durata_stimata = Column(DECIMAL(4, 2), nullable=False, default=0)  # 1=1ora, 1.5=1ora30min
    tipo_intervento = Column(String(20), nullable=False)  # "Meccanico" o "Carrozziere"
    
    # Nuovi campi per gestione stato intervento CMM/CBM
    stato_intervento_id = Column(Integer, ForeignKey("intervention_status_types.id"), nullable=True)
    note_intervento = Column(Text, nullable=True)  # Note generiche sull'intervento
    note_sospensione = Column(Text, nullable=True)  # Nota obbligatoria se stato = "sospeso"
    ore_effettive = Column(DECIMAL(5, 2), nullable=True)  # Ore effettivamente impiegate
    data_inizio = Column(DateTime(timezone=True), nullable=True)  # Data/ora inizio lavorazione
    data_fine = Column(DateTime(timezone=True), nullable=True)  # Data/ora fine lavorazione
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    work_order = relationship("WorkOrder", back_populates="interventions")
    stato_intervento = relationship("InterventionStatusType")
    
    def __repr__(self):
        return f"<Intervention(work_order_id={self.work_order_id}, progressivo={self.progressivo}, tipo={self.tipo_intervento})>"
