import sqlalchemy as sq
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from config import db_owner, db_password, db_name


engine = sq.create_engine(f'postgresql+psycopg2://{db_owner}:{db_password}@localhost:5432/{db_name}')
Base = declarative_base()
Session = sessionmaker(bind=engine)

# Надо не забыть сделать проверку на наличие каких-либо данных уже в бд!!!


class BotUser(Base):
    __tablename__ = 'bot_user'

    # id = sq.Column(sq.Integer, unique=True)
    vk_id = sq.Column(sq.Integer, primary_key=True)
    found_person = relationship('FoundPerson', back_populates='bot_user')


class FoundPerson(Base):
    # Нужно сделать ключ = ид человека + ид того, кто его нашёл
    __tablename__ = 'found_person'

    id = sq.Column(sq.Integer, primary_key=True)
    id_vk_bot_user = sq.Column(sq.Integer, sq.ForeignKey('bot_user.vk_id'), primary_key=True)
    # id_bot_user = sq.Column(sq.Integer, sq.ForeignKey('bot_user.id'))
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


if __name__ == '__main__':
    pass
    # Init scheme
    # Инициализация схемы в бд (создаются все таблицы, но сама БД должна быть уже создана)
    # Base.metadata.create_all(engine)

    # Сначала открываем сессию, потом записываем в неё данные (.add), а затем заносим их в БД (.commit)
    # session = Session()

    # user1 = BotUser(vk_id=11)
    # session.add(user1)
    # session.commit()
    # vk_id_profile111 = FoundPerson(id=111, id_vk_bot_user=88)
    # session.add(vk_id_profile111)
    # session.commit()
