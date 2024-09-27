# Импорт необходимых модулей
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Boolean,
    Text,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime

engine = create_engine("sqlite:///bot_database.db", echo=True)
Base = declarative_base()

Session = sessionmaker(bind=engine)
session = Session()


# Таблица пользователей (менеджеров, администраторов)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    role = Column(String)  # 'manager' или 'administrator'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tasks = relationship("Task", back_populates="user")


# Таблица интеграций (CRM системы, мессенджеры)
class Integration(Base):
    __tablename__ = "integrations"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    type = Column(String)  # 'CRM' или 'Messenger'
    settings = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    contact_sources = relationship("ContactSource", back_populates="integration")
    messengers = relationship("Messenger", back_populates="integration")
    tasks = relationship("Task", back_populates="crm")


# Таблица сегментов (групп контактов)
class Segment(Base):
    __tablename__ = "segments"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    contacts = relationship("Contact", back_populates="segment")


# Таблица источников контактов
class ContactSource(Base):
    __tablename__ = "contact_sources"

    id = Column(Integer, primary_key=True)
    name = Column(String)  # Например, 'Ручная загрузка', 'AmoCRM'
    integration_id = Column(Integer, ForeignKey("integrations.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    contacts = relationship("Contact", back_populates="source")
    integration = relationship("Integration", back_populates="contact_sources")


# Таблица контактов (клиентов)
class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    phone = Column(String)
    email = Column(String)
    source_id = Column(Integer, ForeignKey("contact_sources.id"))
    segment_id = Column(Integer, ForeignKey("segments.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    source = relationship("ContactSource", back_populates="contacts")
    segment = relationship("Segment", back_populates="contacts")
    conversations = relationship("Conversation", back_populates="contact")
    tasks = relationship("Task", back_populates="contact")


# Таблица сценариев бота
class BotScript(Base):
    __tablename__ = "bot_scripts"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    conversations = relationship("Conversation", back_populates="script")


# Таблица мессенджеров
class Messenger(Base):
    __tablename__ = "messengers"

    id = Column(Integer, primary_key=True)
    name = Column(String)  # Например, 'ChatApp', 'Umnico'
    integration_id = Column(Integer, ForeignKey("integrations.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    conversations = relationship("Conversation", back_populates="messenger")
    integration = relationship("Integration", back_populates="messengers")


# Таблица переписок (общение бота с клиентами)
class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"))
    messenger_id = Column(Integer, ForeignKey("messengers.id"))
    script_id = Column(Integer, ForeignKey("bot_scripts.id"))
    status = Column(String)  # Например, 'active', 'completed'
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)

    contact = relationship("Contact", back_populates="conversations")
    messenger = relationship("Messenger", back_populates="conversations")
    script = relationship("BotScript", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")


# Таблица сообщений в переписке
class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    sender = Column(String)  # 'bot' или 'client'
    message_text = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_ai_generated = Column(Boolean, default=False)

    conversation = relationship("Conversation", back_populates="messages")


# Таблица задач для менеджеров
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    crm_id = Column(Integer, ForeignKey("integrations.id"))  # CRM система
    description = Column(Text)
    status = Column(String)  # Например, 'new', 'in_progress', 'completed'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    contact = relationship("Contact", back_populates="tasks")
    user = relationship("User", back_populates="tasks")
    crm = relationship("Integration", back_populates="tasks")


if __name__ == "__main__":
    Base.metadata.create_all(engine)
