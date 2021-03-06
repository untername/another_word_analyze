"""
Набор классов и конфигов, являющихся важной частью моей поделки.

[AuthService]
    [hash password]:    Хэширование пароля.
    [verify password]:  Сравнение хэшей паролей.
    [create token]:     Создания токена для пользователя.

    :instance: auth_service: Нужен для взаимодействия с классом UserService.

[UserService]
    [get user]:             Поиск юзера по id.
    [get user by email]:    Поиск юзера по почте.
    [get user by username]: Поиск юзера по юзернейму.
    [register user]:        Регистрация пользователя.
    [is authenticated?]:    Авторизация пользователя.
    [update user]:          Обновление информации о пользователе.
    [destroy user]:         Удаление пользователя из бд.

[EmailService]
    [send email]:           Отправить сообщение по почте.
    [email for new user]:   Отправить сообщение новому пользователю.
"""

from fastapi.encoders import jsonable_encoder
from jose import jwt
from passlib.context import CryptContext
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from pydantic import EmailStr
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import emails
from emails.template import JinjaTemplate
from models.users import User
from schemas.users import UserORM, UserCreate, UserBase
from utils.settings import token_config, email_config


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class AuthException(BaseException):
    pass


class AuthService:

    """
    [Authentification]

    Класс, предоставляющий методы для работы с паролем и токеном.
    Был создан для того, чтобы собрать вместе все, связанное с паролем и токеном.
    """

    def get_hash_password(self, *, password: str) -> str:

        """
        [Hash]

        Returns:
            [str]: Возвращает хэшированный пароль.
        """

        return pwd_context.hash(password)

    def verify_password(self, *, user_password: str, hashed_password: str) -> bool:

        """
        [Verify]

        Returns:
            [bool]: Проверяет, совпадают ли хэши паролей. Возвращает True/False.
        """

        return pwd_context.verify(user_password, hashed_password)

    def create_token(self, *, data: Dict, expires_delta: Optional[timedelta] = None) -> str:

        """
        [Token]

        Returns:
            [str]: Возвращает токен.
        """

        to_encode = data.copy()
        expire = datetime.utcnow()
        expire += expires_delta if expires_delta else timedelta(minutes=15)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, token_config.SECRET_KEY, algorithm=token_config.ALGORITHM)

        return encoded_jwt


auth_service = AuthService()


class UserService:

    """
    ['Service' for User]

    Набор методов, нужные для взаимодействия с моделью пользователя.
    """

    def __init__(self, database: Session) -> None:
        self.database = database

    def get_user(self, *, ident: int) -> User:

        """
        [Return User]

        Returns:
            [Dict]: Возвращает пользователя по id.
        """
        return self.database.query(User).get(ident=ident)

    def get_user_by_email(self, *, email: EmailStr) -> User:

        """
        [Return User]

        Нужна для проверки, есть ли в данной бд этот email.

        Returns:
            [Dict]: Возвращает пользователя.
        """

        return self.database.query(User).filter(User.email == email).first()

    def get_user_by_username(self, *, username: str) -> User:

        """
        [Return User]

        Нужен для проверки, есть ли в данной бд этот username.

        Returns:
            [Dict]: Возвращает пользователя.
        """

        return self.database.query(User).filter(User.username == username).first()

    def registrate_user(self, *, data: UserCreate) -> User:

        """
        [Registration]

        Raises:
            [HTTPException]: Райзится при условии, если пользователь с этим email/username уже зарегистрирован.

        Returns:
            [UserORM]: Возвращается созданная модель пользователя, в pydantic-модели.
        """

        message = "User with this {} is already registered"

        if self.get_user_by_email(email=data.email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message.format("mail"))

        if self.get_user_by_username(username=data.username):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message.format("username"))

        hashed = auth_service.get_hash_password(password=data.password)
        user = User(username=data.username, email=data.email, password=hashed)
        self.database.add(user)
        self.database.commit()
        self.database.refresh(user)

        return user

    def is_authenticated_user(self, *, username: str, password: str) -> Optional[UserORM]:

        """
        [Is authenticated?]

        Returns:
            [UserORM]: Возвращает данные о пользователе, если он существует.
            [None]: Возвращает None, если пользователь не найден или хэши паролей не совпадают.
        """

        user = self.get_user_by_username(username=username)
        if not user:
            return None
        if not auth_service.verify_password(user_password=password, hashed_password=user.password):
            return None

        return user

    def update_user(self, *, old_info: UserORM, new_info: UserBase) -> UserORM:

        """
        [Update]

        Returns:
            [UserORM]: Возвращает обновленные данные о пользователе.
        """

        data = jsonable_encoder(old_info)
        to_update = new_info.dict()

        for item in data:
            if item in to_update:
                setattr(old_info, item, to_update[item])

        self.database.add(old_info)
        self.database.commit()
        self.database.refresh(old_info)

        return old_info

    def destroy_user(self, *, username: str) -> User:

        """
        [Delete]

        Returns:
            [User]: Возвращает пользователя, данные которого удалены из бд.
        """

        check = self.database.query(User).filter(User.username == username).first()

        if not check:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This username is not defined")

        self.database.delete(check)
        self.database.commit()

        return check


class EmailService:

    """
    [Email]

    Класс, объединяющий все методы отправки сообщений по почте. Пока их только 2.
    """

    async def send_mail(self, to: str, subject: str = "", template: str = "", environment: Any = {}) -> None:

        """
        [Send]

        Метод, отвечающий за отправку сообщения по почте. Только и всего.
        """

        message = emails.Message(
            subject=JinjaTemplate(subject),
            html=JinjaTemplate(template),
            mail_from=("Untername0", email_config.DEFAULT_FROM_EMAIL))

        settings = {
            "host": email_config.EMAIL_HOST,
            "port": email_config.EMAIL_PORT,
            "user": email_config.EMAIL_HOST_USER,
            "password": email_config.EMAIL_HOST_PASSWORD,
            "tls": email_config.EMAIL_USE_TLS}

        response = message.send(to=to, render=environment, smtp=settings)
        assert response.status_code == 250

    async def email_for_new_user(self, email: str, username: str) -> None:

        """
        [For new]

        Метод, который вызывается при регистрации нового пользователя.
        Делегирует свою работу методу выше.
        """

        title = f"Welcome, {username}"
        url_link = email_config.HTTP_URL

        with open("C:/Proects/API_FastAPI/fast_api_backend/new_user_email.html") as f:
            template = f.read()

        await self.send_mail(
            to=email,
            subject=title,
            template=template,
            environment={
                "project_name": "FastAPI",
                "username": username,
                "email": email,
                "link": url_link})
