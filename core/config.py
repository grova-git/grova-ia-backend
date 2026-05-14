from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Orchestrator SaaS"
    SUPABASE_URL: str
    SUPABASE_KEY: str
    OPENAI_API_KEY: str
    # Clave maestra de verificación para el webhook, aunque luego cada tenant pueda tener la suya
    GLOBAL_WHATSAPP_VERIFY_TOKEN: str 

    class Config:
        env_file = ".env"

settings = Settings()
