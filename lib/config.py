import configparser
import os
from .logger import logger

def load_config():
    """Загружает конфигурацию из файла"""
    config = configparser.ConfigParser()
    
    if not os.path.exists('icersdata.ini'):
        logger.error("Файл конфигурации 'icersdata.ini' не найден!")
        print("📝 Создайте файл со следующим содержимым:")
        print("""
[VK]
token = ваш_токен_доступа
user_id = ваш_user_id
        """)
        exit(1)
    
    config.read('icersdata.ini', encoding='utf-8')
    
    try:
        token = config.get('VK', 'token')
        user_id = config.getint('VK', 'user_id')
        
        if token == 'ваш_токен_доступа' or user_id == 0:
            logger.error("Заполните данные в файле 'icersdata.ini'!")
            exit(1)
            
        return token, user_id
    except Exception as e:
        logger.error(f"Ошибка чтения конфигурации: {e}")
        exit(1)