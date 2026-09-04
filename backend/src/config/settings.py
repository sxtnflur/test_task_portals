from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    database_url: str

    class Config:
        case_sensitive = False


settings = Settings(_env_file='.env', _env_file_encoding='utf-8')
