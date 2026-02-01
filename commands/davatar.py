"""
Команда .davatar - отправляет аватарку пользователя в избранное
"""
import time 

def process_davatar(clean_command, vk, message_id, peer_id, user_id):
    """Обрабатывает .davatar"""
    
    try:
        # Удаляем сообщение команды
        try:
            vk.messages.delete(message_ids=message_id, delete_for_all=1)
        except:
            pass
        
        # Определяем пользователя
        target_user_id = user_id  # По умолчанию себя
        
        # Если есть ответ на сообщение, берем оттуда
        messages = vk.messages.getById(message_ids=[message_id])
        if messages['items']:
            message = messages['items'][0]
            
            if 'reply_message' in message:
                reply_message = message['reply_message']
                target_user_id = reply_message.get('from_id', user_id)
            elif 'fwd_messages' in message and message['fwd_messages']:
                target_user_id = message['fwd_messages'][0].get('from_id', user_id)
        
        # Получаем информацию о пользователе
        user_info = vk.users.get(
            user_ids=target_user_id,
            fields='photo_max_orig,photo_id'
        )[0]
        
        if 'photo_max_orig' not in user_info:
            vk.messages.send(
                peer_id=peer_id,
                message="❌ Не удалось получить аватарку!",
                random_id=0
            )
            return ""
        
        # Отправляем в избранное (себе)
        photo_url = user_info['photo_max_orig']
        
        # Скачиваем фото
        import requests
        import tempfile
        import os
        
        temp_dir = tempfile.gettempdir()
        timestamp = int(time.time())
        photo_file = os.path.join(temp_dir, f"avatar_{timestamp}.jpg")
        
        response = requests.get(photo_url, stream=True, timeout=30)
        if response.status_code == 200:
            with open(photo_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # Загружаем на сервер
            upload_server = vk.photos.getMessagesUploadServer(peer_id=user_id)  # В избранное
            
            with open(photo_file, 'rb') as f:
                files = {'photo': f}
                response = requests.post(upload_server['upload_url'], files=files, timeout=120)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if 'error' not in result:
                        # Сохраняем фото
                        save_result = vk.photos.saveMessagesPhoto(
                            server=result['server'],
                            photo=result['photo'],
                            hash=result['hash']
                        )
                        
                        if save_result and len(save_result) > 0:
                            saved_photo = save_result[0]
                            attachment = f"photo{saved_photo['owner_id']}_{saved_photo['id']}"
                            
                            # Отправляем себе в избранное
                            vk.messages.send(
                                peer_id=user_id,  # Себе!
                                attachment=attachment,
                                message=f"🖼️ Аватарка пользователя {user_info['first_name']} {user_info['last_name']}",
                                random_id=0
                            )
            
            # Удаляем временный файл
            if os.path.exists(photo_file):
                os.remove(photo_file)
        
        # Сообщаем в чат
        vk.messages.send(
            peer_id=peer_id,
            message=f"✅ Аватарка {user_info['first_name']} отправлена в Избранное!",
            random_id=0
        )
        
        return ""
        
    except Exception as e:
        print(f"Ошибка в .davatar: {e}")
        return ""