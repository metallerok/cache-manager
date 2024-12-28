import sqlalchemy as sa
import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Sprint(Base):
    __tablename__ = "sprints"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=lambda: str(uuid.uuid4())
    )

    title: Mapped[str] = mapped_column(nullable=False)


class Task(Base):
    __tablename__ = "tasks"
    __model_version__ = "1"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=lambda: str(uuid.uuid4())
    )

    title: Mapped[str] = mapped_column(nullable=False)

    sprint_id: Mapped[str] = mapped_column(sa.ForeignKey("sprints.id"), index=True)
    sprint: Mapped["Sprint"] = relationship()
