from sqlalchemy import Enum, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import AgentStatus, enum_values


class Agent(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "agents"

    workspace_id: Mapped[str] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        index=True,
    )
    name: Mapped[str] = mapped_column(String(180), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    role: Mapped[str] = mapped_column(String(120), index=True)
    instructions: Mapped[str | None] = mapped_column(Text)
    model_provider: Mapped[str] = mapped_column(
        String(80), default="mock", nullable=False
    )
    model_name: Mapped[str] = mapped_column(String(120), default="mock-control-v1")
    temperature: Mapped[float] = mapped_column(Float, default=0.2, nullable=False)
    status: Mapped[AgentStatus] = mapped_column(
        Enum(AgentStatus, values_callable=enum_values, native_enum=False),
        default=AgentStatus.ACTIVE,
        nullable=False,
        index=True,
    )
