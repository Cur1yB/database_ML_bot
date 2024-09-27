from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import (
    Base,
    User,
    Integration,
    Segment,
    ContactSource,
    Contact,
    BotScript,
    Messenger,
    Conversation,
    Message,
    Task,
)
import factory
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker


fake = Faker("ru_RU")


engine = create_engine("sqlite:///bot_database.db")
Session = sessionmaker(bind=engine)
session = Session()


class BaseFactory(SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session = session
        sqlalchemy_session_persistence = "commit"


# Фабрика для пользователей
class UserFactory(BaseFactory):
    class Meta:
        model = User

    name = factory.LazyAttribute(lambda x: fake.name())
    email = factory.LazyAttribute(lambda x: fake.email())
    role = factory.Iterator(["manager", "administrator"])
    created_at = factory.LazyFunction(fake.date_time_between_dates)
    updated_at = factory.LazyFunction(fake.date_time_between_dates)


# Фабрика для интеграций
class IntegrationFactory(BaseFactory):
    class Meta:
        model = Integration

    name = factory.Iterator(["AmoCRM", "Bitrix24", "GetCourse", "ChatApp", "Umnico"])
    type = factory.Iterator(["CRM", "Messenger"])
    settings = factory.LazyAttribute(lambda x: fake.text(max_nb_chars=50))
    is_active = True
    created_at = factory.LazyFunction(fake.date_time_between_dates)
    updated_at = factory.LazyFunction(fake.date_time_between_dates)


# Фабрика для сегментов
class SegmentFactory(BaseFactory):
    class Meta:
        model = Segment

    name = factory.LazyAttribute(lambda x: f"Сегмент {fake.word().capitalize()}")
    description = factory.LazyAttribute(lambda x: fake.sentence())
    created_at = factory.LazyFunction(fake.date_time_between_dates)
    updated_at = factory.LazyFunction(fake.date_time_between_dates)


# Фабрика для источников контактов
class ContactSourceFactory(BaseFactory):
    class Meta:
        model = ContactSource

    name = factory.Iterator(["Ручная загрузка", "AmoCRM", "Bitrix24"])
    integration = factory.SubFactory(IntegrationFactory, type="CRM")
    created_at = factory.LazyFunction(fake.date_time_between_dates)
    updated_at = factory.LazyFunction(fake.date_time_between_dates)


# Фабрика для контактов
class ContactFactory(BaseFactory):
    class Meta:
        model = Contact

    name = factory.LazyAttribute(lambda x: fake.name())
    phone = factory.LazyAttribute(lambda x: fake.phone_number())
    email = factory.LazyAttribute(lambda x: fake.email())
    source = factory.SubFactory(ContactSourceFactory)
    segment = factory.SubFactory(SegmentFactory)
    created_at = factory.LazyFunction(fake.date_time_between_dates)
    updated_at = factory.LazyFunction(fake.date_time_between_dates)


# Фабрика для сценариев бота
class BotScriptFactory(BaseFactory):
    class Meta:
        model = BotScript

    name = factory.LazyAttribute(lambda x: f"Сценарий {fake.word().capitalize()}")
    content = factory.LazyAttribute(lambda x: fake.paragraph(nb_sentences=5))
    created_at = factory.LazyFunction(fake.date_time_between_dates)
    updated_at = factory.LazyFunction(fake.date_time_between_dates)


# Фабрика для мессенджеров
class MessengerFactory(BaseFactory):
    class Meta:
        model = Messenger

    name = factory.Iterator(["ChatApp", "Umnico", "WhatsApp", "Telegram"])
    integration = factory.SubFactory(IntegrationFactory, type="Messenger")
    is_active = True
    created_at = factory.LazyFunction(fake.date_time_between_dates)
    updated_at = factory.LazyFunction(fake.date_time_between_dates)


# Фабрика для переписок
class ConversationFactory(BaseFactory):
    class Meta:
        model = Conversation

    contact = factory.SubFactory(ContactFactory)
    messenger = factory.SubFactory(MessengerFactory)
    script = factory.SubFactory(BotScriptFactory)
    status = factory.Iterator(["active", "completed"])
    started_at = factory.LazyFunction(fake.date_time_between_dates)
    ended_at = factory.Maybe(
        "status",
        yes_declaration=factory.LazyFunction(fake.date_time_between_dates),
        no_declaration=None,
    )


# Фабрика для сообщений
class MessageFactory(BaseFactory):
    class Meta:
        model = Message

    conversation = factory.SubFactory(ConversationFactory)
    sender = factory.Iterator(["bot", "client"])
    message_text = factory.LazyAttribute(lambda x: fake.sentence(nb_words=10))
    timestamp = factory.LazyFunction(fake.date_time_between_dates)
    is_ai_generated = factory.LazyAttribute(lambda x: x.sender == "bot")


# Фабрика для задач
class TaskFactory(BaseFactory):
    class Meta:
        model = Task

    contact = factory.SubFactory(ContactFactory)
    user = factory.SubFactory(UserFactory, role="manager")
    crm = factory.SubFactory(IntegrationFactory, type="CRM")
    description = factory.LazyAttribute(lambda x: fake.sentence())
    status = factory.Iterator(["new", "in_progress", "completed"])
    created_at = factory.LazyFunction(fake.date_time_between_dates)
    updated_at = factory.LazyFunction(fake.date_time_between_dates)


# Функция для заполнения базы данных
def populate_database():
    users = UserFactory.create_batch(5)
    crm_integrations = IntegrationFactory.create_batch(2, type="CRM")
    messenger_integrations = IntegrationFactory.create_batch(2, type="Messenger")
    segments = SegmentFactory.create_batch(3)
    contact_sources = ContactSourceFactory.create_batch(3)
    contacts = ContactFactory.create_batch(20)
    scripts = BotScriptFactory.create_batch(2)
    messengers = MessengerFactory.create_batch(3)
    conversations = ConversationFactory.create_batch(15)
    for conversation in conversations:
        MessageFactory.create_batch(10, conversation=conversation)
    tasks = TaskFactory.create_batch(10)


# Функция заполнения базы данных
if __name__ == "__main__":
    Base.metadata.create_all(engine)
    populate_database()

    print("База данных успешно заполнена случайными данными.")
