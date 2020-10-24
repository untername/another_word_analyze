from pydantic import BaseSettings


class TokenConfig(BaseSettings):

    SECRET_KEY: str = "70c20c52a3bf1e67ef6492ec77d45f748898cdc423adef4fd00dd587cce43ae4"
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


class EmailConfig(BaseSettings):

    EMAIL_HOST: str = 'smtp.sendgrid.net'
    EMAIL_HOST_USER: str = ''
    EMAIL_HOST_PASSWORD: str = ''
    EMAIL_PORT: int = 0 
    EMAIL_USE_TLS: bool = True
    DEFAULT_FROM_EMAIL: str = ''

    HTTP_URL: str = "http://localhost:8000/me"


token_config = TokenConfig()
email_config = EmailConfig()
