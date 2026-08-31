from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SECRET_KEY: str = Field(default="dev-secret-key-change-me") 
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = Field(default="sqlite:///./dev_database.db")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()