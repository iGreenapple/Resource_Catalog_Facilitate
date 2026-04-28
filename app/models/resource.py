"""SQLAlchemy modely a relace pro Resource Catalogue tabulky."""

from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


resource_audiences = Table(
    "resource_audiences",
    Base.metadata,
    Column("resource_id", ForeignKey("resources.resource_id", ondelete="CASCADE"), primary_key=True),
    Column("audience_code", ForeignKey("audiences.code"), primary_key=True),
)

resource_tasks = Table(
    "resource_tasks",
    Base.metadata,
    Column("resource_id", ForeignKey("resources.resource_id", ondelete="CASCADE"), primary_key=True),
    Column("task_code", ForeignKey("tasks.code"), primary_key=True),
)

resource_stages = Table(
    "resource_stages",
    Base.metadata,
    Column("resource_id", ForeignKey("resources.resource_id", ondelete="CASCADE"), primary_key=True),
    Column("stage_code", ForeignKey("stages.code"), primary_key=True),
)

resource_personas = Table(
    "resource_personas",
    Base.metadata,
    Column("resource_id", ForeignKey("resources.resource_id", ondelete="CASCADE"), primary_key=True),
    Column("persona_code", ForeignKey("personas.code"), primary_key=True),
)

resource_keywords = Table(
    "resource_keywords",
    Base.metadata,
    Column("resource_id", ForeignKey("resources.resource_id", ondelete="CASCADE"), primary_key=True),
    Column("keyword_id", ForeignKey("keywords.id", ondelete="CASCADE"), primary_key=True),
)


class Resource(Base):
    __tablename__ = "resources"

    resource_id = Column(String(50), primary_key=True)
    title = Column(Text, nullable=False)
    url = Column(Text, nullable=False)
    short_description = Column(Text, nullable=False)
    resource_type = Column(String(100), nullable=False)
    effort_level = Column(String(100), nullable=False)
    practicality_level = Column(String(200), nullable=False)
    language = Column(String(20), nullable=False)
    keywords_tags = relationship("Keyword", secondary=resource_keywords)
    topic_area = Column(String(200), nullable=False)
    recommended_rank = Column(Integer, nullable=True)
    featured_m6 = Column(Boolean, nullable=False, default=False)
    quality_note = Column(Text, nullable=False)
    source_owner_org = Column(Text, nullable=False)
    source_year_or_last_update = Column(String(20), nullable=False)
    access_conditions = Column(String(100), nullable=False)
    contributor_partner = Column(String(200), nullable=False)
    review_status = Column(String(100), nullable=False)
    review_due_date = Column(Date, nullable=False)
    last_checked_date = Column(Date, nullable=False)
    editor_notes = Column(Text, nullable=False, default="")

    audience = relationship("Audience", secondary=resource_audiences)
    mapped_tasks = relationship("Task", secondary=resource_tasks)
    mapped_stages = relationship("Stage", secondary=resource_stages)
    mapped_personas = relationship("Persona", secondary=resource_personas)


class Audience(Base):
    __tablename__ = "audiences"
    code = Column(String(100), primary_key=True)


class Task(Base):
    __tablename__ = "tasks"
    code = Column(String(20), primary_key=True)


class Stage(Base):
    __tablename__ = "stages"
    code = Column(String(100), primary_key=True)


class Persona(Base):
    __tablename__ = "personas"
    code = Column(String(100), primary_key=True)


class Keyword(Base):
    __tablename__ = "keywords"
    id = Column(Integer, primary_key=True)
    keyword = Column(String(200), unique=True, nullable=False)
