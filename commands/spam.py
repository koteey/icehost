"""
Команда .spam - спам сообщениями
"""

import time
import threading

def process(clean_command, vk, peer_id, user_id):
    """Обрабатывает команду .spam"""
    
    parts = clean_command.split()
    if len(parts) < 3:
        return ""
    
    try:
        count = int(parts[1])
        delay = float(parts[2])
        text = ' '.join(parts[3:]) if len(parts) > 3 else "Спам сообщение"
        
        # Проверяем параметры
        if count <= 0 or count > 50 or delay < 0.1 or delay > 10:
            return ""
        
        # Запускаем спам в отдельном потоке
        def spam_thread():
            for _ in range(count):  # Убрали счетчик i
                try:
                    vk.messages.send(
                        peer_id=peer_id,
                        message=text,  # Без счетчика
                        random_id=0
                    )
                    time.sleep(delay)
                except:
                    pass
        
        thread = threading.Thread(target=spam_thread)
        thread.daemon = True
        thread.start()
        
        return ""
        
    except:
        return ""