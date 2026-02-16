"""
Work Order Audit model for tracking state transitions and workflow history
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.work_order import WorkOrderStatus
import enum


class TransitionType(str, enum.Enum):
    """Type of state transition"""
    MANUAL = "manual"              # Manual transition by user
    AUTOMATIC = "automatic"        # Automatic transition by system
    ROLLBACK = "rollback"          # Rollback to previous state


class WorkOrderAudit(Base):
    """Audit trail for work order state transitions"""
    __tablename__ = "work_order_audits"
    
    id = Column(Integer, primary_key=True, index=True)
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False, index=True)
    
    # State transition info
    from_state = Column(Enum(WorkOrderStatus), nullable=False)
    to_state = Column(Enum(WorkOrderStatus), nullable=False)
    transition_type = Column(Enum(TransitionType), default=TransitionType.MANUAL)
    
    # User info
    executed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    user_role = Column(String(50))  # Role of the user at time of transition (for historical record)
    
    # Reason and notes
    reason = Column(Text, nullable=True)  # Why the transition happened
    notes = Column(Text, nullable=True)   # Additional notes
    
    # System info
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(String(500), nullable=True)  # Browser/client info
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    work_order = relationship("WorkOrder", backref="audit_trail")
    executor = relationship("User", foreign_keys=[executed_by])
    
    def __repr__(self):
        return f"<WorkOrderAudit(work_order_id={self.work_order_id}, {self.from_state} → {self.to_state})>"
