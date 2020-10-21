from sqlalchemy import Column, String, Integer
from core.database import DataBase


class User(DataBase):

    """
    [Base]

    Модель пользователя в БД.
    :param: password - хэш пароля, который и будет использоваться при последующей авторизации.
    """

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)
