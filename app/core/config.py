from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "POTG"
    APP_ENV: str = "development"
    APP_VERSION: str = "0.1.0"

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 7
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    RESET_PASSWORD_TOKEN_EXPIRE_MINUTES: int = 15

    # Database
    DATABASE_URL: str

    # Email (Gmail SMTP)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASSWORD: str
    EMAIL_FROM: str
    EMAIL_FROM_NAME: str = "POTG App"

    # Cloudinary
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    # Mux Video
    MUX_TOKEN_ID: str = ""
    MUX_TOKEN_SECRET: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()
