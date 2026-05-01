from sqlalchemy import JSON, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import ExecutionStatus, LogLevel, WorkflowStatus, enum_values


class Workflow(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "workflows"

    workspace_id: Mapped[str] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        index=True,
    )
    name: Mapped[str] = mapped_column(String(180), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[WorkflowStatus] = mapped_column(
        Enum(WorkflowStatus, values_callable=enum_values, native_enum=False),
        default=WorkflowStatus.DRAFT,
        nullable=False,
        index=True,
    )
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))


class WorkflowStep(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "workflow_steps"

    workflow_id: Mapped[str] = mapped_column(
        ForeignKey("workflows.id", ondelete="CASCADE"),
        index=True,
    )
    step_order: Mapped[int] = mapped_column(Integer, index=True)
    name: Mapped[str] = mapped_column(String(180))
    step_type: Mapped[str] = mapped_column(String(80), index=True)
    config: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class Execution(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "executions"

    workspace_id: Mapped[str] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        index=True,
    )
    workflow_id: Mapped[str | None] = mapped_column(
        ForeignKey("workflows.id", ondelete="SET NULL"),
        index=True,
    )
    status: Mapped[ExecutionStatus] = mapped_column(
        Enum(ExecutionStatus, values_callable=enum_values, native_enum=False),
        default=ExecutionStatus.QUEUED,
        nullable=False,
        index=True,
    )
    trigger: Mapped[str] = mapped_column(String(80), default="manual")
    result: Mapped[dict | None] = mapped_column(JSON)
    error_message: Mapped[str | None] = mapped_column(Text)
    duration_ms: Mapped[int | None] = mapped_column(Integer)


class ExecutionLog(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "execution_logs"

    execution_id: Mapped[str] = mapped_column(
        ForeignKey("executions.id", ondelete="CASCADE"),
        index=True,
    )
    level: Mapped[LogLevel] = mapped_column(
        Enum(LogLevel, values_callable=enum_values, native_enum=False),
        default=LogLevel.INFO,
        nullable=False,
        index=True,
    )
    message: Mapped[str] = mapped_column(String(500))
    metadata_json: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
