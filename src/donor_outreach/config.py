from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppSettings(BaseSettings):

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    log_level: str = "DEBUG"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/donor_outreach"
    test_database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/donor_outreach_test"
    aws_profile: str = "default"
    aws_region: str = "us-east-1"
    
def get_settings() -> AppSettings:
    return AppSettings()


    # DonorOutreachComprehendTranslatePolicy