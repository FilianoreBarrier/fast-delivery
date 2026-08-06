from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Fast Delivery"
    debug: bool = True
    database_url: str = ""

    cors_origins: list[str] = [
        "http://localhost:5177",
        "http://127.0.0.1:5177",
        "http://localhost:3001",
        "http://127.0.0.1:3001"
    ]

    secret_key: str = ""
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }


settings = Settings()
