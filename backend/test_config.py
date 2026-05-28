# backend/test_config.py
from config import load_Settings

def test_valid_config():
    s = load_Settings()
    assert s.PORTAINER_API_URL.startswith('https://')
    assert len(s.PORTAINER_API_KEY) > 10
    assert len(s.ALLOWED_CONTAINER_NAMES.split(',')) >= 1
    print('✅ All validations passed')

if __name__ == '__main__':
    test_valid_config()
