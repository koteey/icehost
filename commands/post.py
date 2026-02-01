"""
Команда .post - опубликовать запись на стене
"""

import os
import tempfile
import time
import requests
from lib.media_utils import get_attachment_info

def process(clean_command, vk, message_id, peer_id, user_id):
    """Обрабатывает команду .post с поддержкой фото"""
    
    try:
        # Сразу удаляем сообщение с командой
        try:
            vk.messages.delete(
                message_ids=message_id,
                delete_for_all=1
            )
        except:
            pass
        
        messages = vk.messages.getById(message_ids=[message_id])
        if not messages['items']:
            return ""
        
        message = messages['items'][0]
        
        # Получаем текст
        text = ""
        if len(clean_command) > 5:
            text = clean_command[5:].strip()
        
        # Ищем фото в сообщении
        photo_attachments = []
        if 'attachments' in message:
            for att in message['attachments']:
                if att['type'] == 'photo':
                    photo_attachments.append(att)
        
        # Ищем фото в ответе
        if 'reply_message' in message:
            reply_message = message['reply_message']
            if 'attachments' in reply_message:
                for att in reply_message['attachments']:
                    if att['type'] == 'photo':
                        photo_attachments.append(att)
        
        # Если нет текста и фото
        if not text and not photo_attachments:
            return ""
        
        if photo_attachments:
            # Загружаем фото на сервер
            upload_server = vk.photos.getWallUploadServer()
            upload_url = upload_server['upload_url']
            
            # Берем первую фотографию
            photo_att = photo_attachments[0]
            att_info = get_attachment_info(photo_att)
            
            if 'url' not in att_info:
                return ""
            
            # Создаем временный файл
            temp_dir = tempfile.gettempdir()
            timestamp = int(time.time())
            temp_photo = os.path.join(temp_dir, f"wall_photo_{timestamp}.jpg")
            
            # Скачиваем фото
            try:
                response = requests.get(att_info['url'], stream=True, timeout=30)
                if response.status_code == 200:
                    with open(temp_photo, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    
                    # Загружаем на сервер
                    with open(temp_photo, 'rb') as f:
                        files = {'photo': f}
                        response = requests.post(upload_url, files=files, timeout=120)
                        
                        if response.status_code != 200:
                            return ""
                        
                        upload_result = response.json()
                        
                        if 'error' in upload_result:
                            return ""
                        
                        # Сохраняем фото на стене
                        save_result = vk.photos.saveWallPhoto(
                            server=upload_result['server'],
                            photo=upload_result['photo'],
                            hash=upload_result['hash']
                        )
                        
                        if not save_result or len(save_result) == 0:
                            return ""
                        
                        saved_photo = save_result[0]
                        attachments = f"photo{saved_photo['owner_id']}_{saved_photo['id']}"
                        
                        # Публикуем запись с фото
                        vk.wall.post(message=text, attachments=attachments)
            finally:
                # Удаляем временный файл
                if os.path.exists(temp_photo):
                    try:
                        os.remove(temp_photo)
                    except:
                        pass
        else:
            # Публикуем только текст
            vk.wall.post(message=text)
        
        return ""
        
    except:
        return ""