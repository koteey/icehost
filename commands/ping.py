import time
from lib.system_utils import get_uptime, get_connection_quality
from lib.vk_utils import measure_network_latency

def process(vk, settings):
    """Обрабатывает команду .ping"""
    style = settings['ping_style']
    
    if style == 'custom':
        return generate_custom_ping(vk, settings)
    elif style == 'detailed':
        return generate_detailed_ping(vk)
    elif style == 'simple':
        return generate_simple_ping()
    elif style == 'network':
        return generate_network_ping(vk)
    else:
        return generate_custom_ping(vk, settings)

def generate_custom_ping(vk, settings):
    """Генерирует кастомное сообщение .ping"""
    try:
        latency = measure_network_latency(vk)
        if latency is None:
            return "❌ Не удалось измерить задержку"
        
        template = settings['custom_messages']['ping']
        
        # Заменяем переменные
        message = template.format(
            ping=f"{latency:.2f}",
            uptime=get_uptime(),
            quality=get_connection_quality(latency),
            timestamp=time.strftime("%H:%M:%S"),
            status="Активен ✅"
        )
        
        return message
    except Exception as e:
        return f"❌ Ошибка в кастомном сообщении: {str(e)}"

def generate_detailed_ping(vk):
    """Детальный пинг"""
    latency = measure_network_latency(vk)
    if latency is not None:
        return f"""🏓 **Детальный пинг**

🌐 Сетевая задержка: `{latency:.2f}ms`
⏱️ Аптайм: {get_uptime()}
✅ Статус: Бот активен
📊 Качество: {get_connection_quality(latency)}"""
    else:
        return "❌ Не удалось измерить задержку"

def generate_simple_ping():
    """Простой пинг"""
    return f"""🔄 **Пинг**

✅ Бот активен
⏱️ Аптайм: {get_uptime()}"""

def generate_network_ping(vk):
    """Сетевой пинг"""
    latency = measure_network_latency(vk)
    if latency is not None:
        return f"""🌐 **Сетевой пинг**

Задержка до API VK: `{latency:.2f}ms`
Качество: {get_connection_quality(latency)}"""
    else:
        return "❌ Не удалось измерить задержку"