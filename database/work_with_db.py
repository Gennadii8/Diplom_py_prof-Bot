import sqlalchemy as sq
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from config import db_owner, db_password, db_name


engine = sq.create_engine(f'postgresql+psycopg2://{db_owner}:{db_password}@localhost:5432/{db_name}')
Base = declarative_base()
Session = sessionmaker(bind=engine)


class BotUser(Base):
    __tablename__ = 'bot_user'

    vk_id = sq.Column(sq.Integer, primary_key=True)
    found_person = relationship('FoundPerson', back_populates='bot_user')


class FoundPerson(Base):
    # ключ = ид найденного человека + ид того, кто его нашёл (юзера бота)
    __tablename__ = 'found_person'

    id = sq.Column(sq.Integer, primary_key=True)
    id_vk_bot_user = sq.Column(sq.Integer, sq.ForeignKey('bot_user.vk_id'), primary_key=True)
    bot_user = relationship(BotUser)


def add_founded_pers(input_user_id, input_founded_profiles):
    Base.metadata.create_all(engine)
    session = Session()
    for one_pers in input_founded_profiles:
        vk_id_profile = FoundPerson(id=one_pers, id_vk_bot_user=input_user_id)
        session.add(vk_id_profile)
    session.commit()


def add_user(input_vk_user_id):
    Base.metadata.create_all(engine)
    session = Session()
    user = BotUser(vk_id=input_vk_user_id)
    session.add(user)
    session.commit()
