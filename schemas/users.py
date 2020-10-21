from pydantic import BaseModel, EmailStr
from typing import Optional


class UserBase(BaseModel):

    """
    [Base]

    Базовая pydantic-модель пользователя.
    """

    username: str
    email: Optional[EmailStr] = None


class UserCreate(UserBase):

    """
    [Create]

    pydantic-модель для создания нового пользователя.
    """

    email: EmailStr
    password: str


class UserORM(UserBase):

    """
    [ORM]

    pydantic-модель для отображения данных пользователя, взятых из БД.
    """

    id: int

    class Config:
        orm_mode = True
