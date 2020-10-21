from pydantic import BaseModel


class Token(BaseModel):

    """
    [Base]

    Pydantic-модель токена. Включает в себя сам токен и его тип (Bearer).
    """

    access_token: str
    token_type: str


class TokenData(BaseModel):

    """
    [Data]

    Pydantic-модель данных о токене.
    :param: sub[username] - пользователь, к которому токен и привязывается.
    """

    sub: str
