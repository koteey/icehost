import os
import sys
import subprocess
import time as time_module

def process(vk, peer_id, message_id):
    """Обрабатывает команду .restart"""
    result_message = """🔄 **Перезапуск бота...**

⏳ Бот будет перезапущен через 3 секунды.

📝 **Сохраните все важные данные!**

Подготовка к перезапуску..."""
    
    # Отправляем сообщение
    vk.messages.edit(
        peer_id=peer_id,
        message_id=message_id,
        message=result_message
    )
    
    # Даем время на чтение
    time_module.sleep(3)
    
    # Пытаемся перезапуститься
    try:
        # Windows
        if os.name == 'nt':
            subprocess.Popen(['python', 'icers.py'])
        # Linux/Mac
        else:
            os.execv(sys.executable, ['python3'] + sys.argv)
        os._exit(0)
    except:
        os._exit(0)
    
    return result_message