"""
Модуль с кастомным классом аутентификации.

[AuthWithCookie]
    [__init__]
    [__call__]
"""

from fastapi import HTTPException, Request, status
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.openapi.models import OAuthFlows
from typing import Dict, Optional


class AuthWithCookie(OAuth2):

    """
    [Auth]:  Класс аутентификации.

    Имеет много общего с OAuth2PasswordBearer, но есть важное отличие:
    Вместо получения токена из заголовка, мы получаем его из файла cookie.
    """

    def __init__(self, tokenUrl: str, scheme_name: Optional[str] = None, scopes: Dict = None, auto_error: bool = True) -> None:

        if not scopes:
            scopes: Dict = {}

        flows = OAuthFlows(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:

        auth_cookie: str = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(auth_cookie)

        if not auth_cookie or scheme.lower() != 'bearer':
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"})
            else:
                return None

        return param
