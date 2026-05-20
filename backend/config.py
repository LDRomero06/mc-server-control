from pydantic import BaseSettings

class Settings(BaseSettings):
    # Replace with your actual Portainer API details
    PORTAINER_API_URL: str
    PORTAINER_API_KEY: str
    # Comma-separated list of allowed server container names
    ALLOWED_CONTAINER_NAMES: str

    class Config:
        env_file = ".env"

def load_settings():
    """Loads configuration from environment variables or .env file."""
    try:
        from pydantic import ValidationError
        settings = Settings()
        print("✅ Configuration loaded successfully.")
        return settings
    except ValidationError as e:
        print(f"❌ Configuration Validation Error: Please ensure your .env file is correct.")
        print(e)
        exit(1)
    except Exception as e:
        print(f"❌ Failed to load settings. Check if your .env file exists and is valid. Error: {e}")
        exit(1)