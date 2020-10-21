from pydantic import BaseSettings


class TokenConfig(BaseSettings):

    SECRET_KEY: str = "70c20c52a3bf1e67ef6492ec77d45f748898cdc423adef4fd00dd587cce43ae4"
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


config = TokenConfig()
