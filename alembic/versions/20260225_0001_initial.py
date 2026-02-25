"""initial schema

Revision ID: 20260225_0001
Revises: 
Create Date: 2026-02-25 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20260225_0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


user_role = sa.Enum('STUDENT', 'INVIGILATOR', name='user_role')
session_status = sa.Enum('SCHEDULED', 'ACTIVE', 'COMPLETED', name='session_status')
alert_severity = sa.Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='alert_severity')


def upgrade() -> None:
    bind = op.get_bind()
    user_role.create(bind, checkfirst=True)
    session_status.create(bind, checkfirst=True)
    alert_severity.create(bind, checkfirst=True)

    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('role', user_role, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    op.create_table(
        'exam_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('exam_name', sa.String(length=255), nullable=False),
        sa.Column('status', session_status, nullable=False),
        sa.Column('student_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('invigilator_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['invigilator_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['student_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'alerts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('exam_session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('severity', alert_severity, nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['exam_session_id'], ['exam_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_alerts_exam_session_id'), 'alerts', ['exam_session_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_alerts_exam_session_id'), table_name='alerts')
    op.drop_table('alerts')
    op.drop_table('exam_sessions')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')

    bind = op.get_bind()
    alert_severity.drop(bind, checkfirst=True)
    session_status.drop(bind, checkfirst=True)
    user_role.drop(bind, checkfirst=True)
