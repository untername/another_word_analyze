from fastapi import Depends, HTTPException, status, Response, Query, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import timedelta
from typing import Dict, List
from models.users import User
from schemas.users import UserCreate, UserORM
from schemas.tokens import TokenData
from schemas.words import Choices
from core.services import UserService, auth_service
from core.database import get_db
from core.authentication import AuthWithCookie
from utils.handlers import text_handler
from utils.settings import config


router = APIRouter()
auth_scheme = AuthWithCookie(tokenUrl='/token')
user_service = UserService(database=get_db())


async def get_current_user(token: str = Depends(auth_scheme), database: Session = Depends(get_db)) -> User:

    """
    [Current User | Depend]

    Info:
        Функция-зависимость.
        Не авторизованный пользователь не имеет доступа к некоторым страницам благодаря этой функции.

    Raises:
        HTTPException: Райзится при ошибке авторизации. Возвращает и хедеры.

    Returns:
        [User]: Возвращает пользователя.
    """

    credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Error Authentificate", headers={"WWW-Authenticate": "Bearer"})

    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            raise credentials

        token_data = TokenData(sub=username)
    except JWTError:
        raise credentials

    user = user_service.get_user_by_username(username=token_data.sub)
    if user is None:
        raise credentials

    return user


@router.post('/token', tags=['Token'])
async def login_for_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends()) -> Dict:

    """
    [Login]

    Info:
        Авторизация пользователя.

    Raises:
        HTTPException: Райзится при ошибке авторизации.

    Returns:
        [Dict[str, str]]: Возвращает токен.
        + Добавляет токен в файлы cookie.
    """

    user = user_service.authentificate_user(username=form_data.username, password=form_data.password)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error Authentification",
            headers={"WWW-Authenticate": "Bearer"})

    access_expire = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_token(data={"sub": user.username}, expires_delta=access_expire)

    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True
    )

    return {
        "access_token": access_token
    }


@router.post('/signup', response_model=UserORM, tags=['User'])
async def signup(form_data: UserCreate, database: Session = Depends(get_db)) -> UserORM:

    """
    [Registration]

    Info:
        Функция регистрации пользователя.

    Raises:
        HTTPException: Райзится, если пользователь с данным username уже зарегистирован.

    Returns:
        [UserORM]: Возвращает данные о только что зарегистированном пользователе.
    """

    user = user_service.get_user_by_username(username=form_data.username)
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="username already registered")

    signuped_user = user_service.registrate_user(data=form_data)

    return signuped_user


@router.get('/me', tags=['User'])
async def get_me_info(me: User = Depends(get_current_user)) -> Dict[str, User]:

    """
    [Info]

    Info:
        Функция, доступная лишь авторизованному пользователю.

    Returns:
        [Dict[str, User]]: Возвращает данные о пользователе.
    """

    return {"me": me}


@router.post('/analyze', dependencies=[Depends(get_current_user)], tags=['Analyzing'])
async def send_text_for_analyze(text: str, method: List[Choices] = Query(default=Choices.translate)) -> Dict:

    """
    [Analyze]

    Info:
        Функция, использующая текстовый обработчик. Доступна только авторизованным пользователям.
        Пользователь может выбрать как 1 вариант обработки, так и несколько.

    Returns:
        [Dict] Возвращает результаты анализа текста.
    """

    analyzed = text_handler(method=method, text=text)
    return analyzed
