import os
from dotenv import load_dotenv

# Загружаем .env только если он существует (для локальной разработки)
if os.path.exists('.env'):
    load_dotenv()

class Config:
    # Railway автоматически подставит эти переменные из настроек
    BLAND_API_KEY = os.getenv("BLAND_API_KEY", "")
    EMERGENCY_PHONE = os.getenv("EMERGENCY_PHONE", "")
    
    # Для Railway не делаем жесткую проверку при импорте
    @classmethod
    def validate(cls):
        """Проверка конфигурации при первом использовании"""
        if not cls.BLAND_API_KEY:
            raise ValueError("BLAND_API_KEY not configured! Add it in Railway dashboard.")
        if not cls.EMERGENCY_PHONE:
            raise ValueError("EMERGENCY_PHONE not configured! Add it in Railway dashboard.")
        return True