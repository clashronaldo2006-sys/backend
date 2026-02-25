import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.alert import AlertSeverity
from app.models.exam_session import SessionStatus


class ExamSessionCreate(BaseModel):
    exam_name: str
    student_id: uuid.UUID
    invigilator_id: uuid.UUID | None = None


class ExamSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    exam_name: str
    status: SessionStatus
    student_id: uuid.UUID
    invigilator_id: uuid.UUID | None
    started_at: datetime | None
    ended_at: datetime | None
    created_at: datetime


class AlertCreate(BaseModel):
    severity: AlertSeverity
    event_type: str
    description: str


class AlertRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    exam_session_id: uuid.UUID
    severity: AlertSeverity
    event_type: str
    description: str
    created_at: datetime
