import platform
from lib.system_utils import get_uptime
from lib.vk_utils import measure_network_latency

def process(vk, settings, USER_ID):
    """Обрабатывает команду .info"""
    style = settings['info_style']
    
    if style == 'custom':
        return generate_custom_info(vk, settings, USER_ID)
    elif style == 'full':
        return generate_full_info(vk, USER_ID)
    elif style == 'minimal':
        return generate_minimal_info(vk, USER_ID)
    elif style == 'system':
        return generate_system_info()
    elif style == 'user':
        return generate_user_info(vk, USER_ID)
    elif style == 'bot':
        return generate_bot_info()
    else:
        return generate_custom_info(vk, settings, USER_ID)

def generate_custom_info(vk, settings, USER_ID):
    """Генерирует кастомное сообщение .info"""
    try:
        user_info = vk.users.get(user_ids=USER_ID, fields='online')[0]
        user_name = f"{user_info['first_name']} {user_info['last_name']}"
        online_status = '✅' if user_info.get('online', 0) else '❌'
        
        template = settings['custom_messages']['info']
        
        # Заменяем переменные
        message = template.format(
            user_name=user_name,
            user_id=USER_ID,
            online_status=online_status,
            os_info=f"{platform.system()} {platform.release()}",
            python_version=platform.python_version(),
            architecture=platform.architecture()[0],
            uptime=get_uptime(),
            platform=platform.platform(),
            processor=platform.processor() or 'Не определен'
        )
        
        return message
    except KeyError as e:
        return f"❌ Неизвестная переменная в шаблоне: {e}\nИспользуйте .settings vars для списка переменных"
    except Exception as e:
        return f"❌ Ошибка в кастомном сообщении: {str(e)}"

def generate_full_info(vk, USER_ID):
    """Полная информация"""
    try:
        user_info = vk.users.get(user_ids=USER_ID, fields='online,last_seen,status')[0]
        user_name = f"{user_info['first_name']} {user_info['last_name']}"
        
        info_text = f"""👤 **Профиль**
• Имя: {user_name}
• ID: {USER_ID}
• Онлайн: {'✅' if user_info.get('online', 0) else '❌'}

⚙️ **Система**
• ОС: {platform.system()} {platform.release()}
• Python: {platform.python_version()}
• Архитектура: {platform.architecture()[0]}

🤖 **Icers**
• Разработчик: SnowCode
• Версия: 2.0
• Аптайм: {get_uptime()}
• Статус: Активен ✅"""
        return info_text
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"

def generate_minimal_info(vk, USER_ID):
    """Минимальная информация"""
    try:
        user_info = vk.users.get(user_ids=USER_ID, fields='online')[0]
        user_name = f"{user_info['first_name']} {user_info['last_name']}"
        
        info_text = f"""📱 **Icers - Минимальная информация**

👤 {user_name} | ID: {USER_ID}
⚙️ {platform.system()} | Python {platform.python_version()}
⏱️ Аптайм: {get_uptime()}
🤖 Статус: {'🟢 Онлайн' if user_info.get('online', 0) else '🔴 Офлайн'}"""
        return info_text
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"

def generate_system_info():
    """Только системная информация"""
    info_text = f"""⚙️ **Системная информация**

• ОС: {platform.system()} {platform.release()}
• Платформа: {platform.platform()}
• Python: {platform.python_version()}
• Архитектура: {platform.architecture()[0]}
• Процессор: {platform.processor() or 'Не определен'}
• Аптайм: {get_uptime()}"""
    return info_text

def generate_user_info(vk, USER_ID):
    """Только информация о пользователе"""
    try:
        user_info = vk.users.get(user_ids=USER_ID, fields='online,last_seen,status')[0]
        user_name = f"{user_info['first_name']} {user_info['last_name']}"
        
        info_text = f"""👤 **Информация о пользователе**

• Имя: {user_name}
• ID: {USER_ID}
• Онлайн: {'✅ Да' if user_info.get('online', 0) else '❌ Нет'}
• Статус: {user_info.get('status', 'Не установлен')}
• Ссылка: vk.com/id{USER_ID}
• Аптайм бота: {get_uptime()}"""
        return info_text
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"

def generate_bot_info():
    """Только информация о боте"""
    info_text = f"""🤖 **Информация о Icers**

• Разработчик: SnowCode
• Версия: 2.0
• Платформа: VK UserBot
• Функции: Команды + Модули + Настройки
• Аптайм: {get_uptime()}
• Статус: Активен ✅"""
    return info_text