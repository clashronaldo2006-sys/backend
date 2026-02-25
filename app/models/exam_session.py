import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SessionStatus(str, enum.Enum):
    SCHEDULED = 'SCHEDULED'
    ACTIVE = 'ACTIVE'
    COMPLETED = 'COMPLETED'


class ExamSession(Base):
    __tablename__ = 'exam_sessions'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exam_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[SessionStatus] = mapped_column(Enum(SessionStatus, name='session_status'), nullable=False, default=SessionStatus.SCHEDULED)
    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    invigilator_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    student = relationship('User', back_populates='student_sessions', foreign_keys=[student_id])
    invigilator = relationship('User', back_populates='invigilated_sessions', foreign_keys=[invigilator_id])
    alerts = relationship('Alert', back_populates='exam_session', cascade='all, delete-orphan')
