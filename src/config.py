from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    """Settings sub class inheriting from BaseSettings"""
    DATABASE_URL:str
    JWT_SECRET:str
    JWT_ALGORITHM:str
    # DB_SYNC_URL:str
    STRIPE_TEST_SECRET_KEY:str
    WEBHOOK_SECRET:str
    
    model_config=SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

configSettgs=Settings()

#Baseettings autmatically loads environment variables
#configSettgs object will read environment variables