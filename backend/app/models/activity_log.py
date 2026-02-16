"""
Activity log model for tracking system activities
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class ActivityLog(Base):
    """Activity log model"""
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    azione = Column(String(100), nullable=False, index=True)
    entita = Column(String(50), index=True)  # e.g., 'work_order', 'customer', 'vehicle'
    entita_id = Column(Integer, index=True)
    descrizione = Column(Text)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    dettagli = Column(JSON)  # Additional details in JSON format
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="activity_logs")
    
    def __repr__(self):
        return f"<ActivityLog(user_id={self.user_id}, azione='{self.azione}', entita='{self.entita}')>"