from pydantic import BaseSettings


class TokenConfig(BaseSettings):

    SECRET_KEY: str = "70c20c52a3bf1e67ef6492ec77d45f748898cdc423adef4fd00dd587cce43ae4"
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


class EmailConfig(BaseSettings):

    EMAIL_HOST: str = 'smtp.sendgrid.net'
    EMAIL_HOST_USER: str = 'apikey'
    EMAIL_HOST_PASSWORD: str = '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'
    EMAIL_PORT: int = 587
    EMAIL_USE_TLS: bool = True
    DEFAULT_FROM_EMAIL: str = 'kalabala971@gmail.com'

    HTTP_URL: str = "http://localhost:8000/me"


token_config = TokenConfig()
email_config = EmailConfig()
