from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.alert import Alert
from app.models.exam_session import ExamSession, SessionStatus
from app.models.user import User, UserRole
from app.schemas.exam import AlertCreate, AlertRead, ExamSessionCreate, ExamSessionRead

router = APIRouter(prefix='/exam', tags=['exam'])


@router.post('/sessions', response_model=ExamSessionRead, status_code=status.HTTP_201_CREATED)
async def create_exam_session(
    payload: ExamSessionCreate,
    _: User = Depends(require_role(UserRole.INVIGILATOR)),
    db: AsyncSession = Depends(get_db),
) -> ExamSession:
    session = ExamSession(
        exam_name=payload.exam_name,
        student_id=payload.student_id,
        invigilator_id=payload.invigilator_id,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


@router.post('/sessions/{session_id}/start', response_model=ExamSessionRead)
async def start_session(
    session_id: UUID,
    _: User = Depends(require_role(UserRole.INVIGILATOR)),
    db: AsyncSession = Depends(get_db),
) -> ExamSession:
    result = await db.execute(select(ExamSession).where(ExamSession.id == session_id))
    session = result.scalar_one_or_none()
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Session not found')

    session.status = SessionStatus.ACTIVE
    session.started_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(session)
    return session


@router.post('/sessions/{session_id}/alerts', response_model=AlertRead, status_code=status.HTTP_201_CREATED)
async def create_alert(
    session_id: UUID,
    payload: AlertCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Alert:
    result = await db.execute(select(ExamSession).where(ExamSession.id == session_id))
    session = result.scalar_one_or_none()
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Session not found')

    if current_user.role == UserRole.STUDENT and session.student_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not allowed for this session')

    alert = Alert(exam_session_id=session_id, **payload.model_dump())
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    return alert


@router.get('/sessions/{session_id}/alerts', response_model=list[AlertRead])
async def list_alerts(
    session_id: UUID,
    _: User = Depends(require_role(UserRole.INVIGILATOR)),
    db: AsyncSession = Depends(get_db),
) -> list[Alert]:
    result = await db.execute(select(Alert).where(Alert.exam_session_id == session_id).order_by(Alert.created_at.desc()))
    return list(result.scalars().all())
