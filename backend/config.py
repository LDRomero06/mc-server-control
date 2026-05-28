from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Replace with your actual Portainer API details
    PORTAINER_API_URL: str 
    PORTAINER_API_KEY: str
    # Comma-separated list of allowed server container names
    ALLOWED_CONTAINER_NAMES: str
    ENDPOINT_ID: str  # Default endpoint ID
    ENDPOINT_RESOURCE: str = "docker"  # Resource type (docker, kubernetes, etc.)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

def load_Settings():
    """Loads configuration from environment variables or .env file."""
    try:
        from pydantic import ValidationError
        s = Settings()
        print("✅ Configuration loaded successfully.")
        return s
    except ValidationError as e:
        print("❌ Configuration Validation Error: Please ensure your .env file is correct.")
        print(e)
        exit(1)
    except Exception as e:
        print(f"❌ Failed to load Settings. Check if your .env file exists and is valid. Error: {e}")
        exit(1)

# Global settings instance loaded on import
settings = load_Settings()
