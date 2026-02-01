"""
Команда .meme / .мем - создание мемов
"""

import os
import tempfile
import time
import requests
from PIL import Image, ImageDraw, ImageFont
from lib.media_utils import get_attachment_info

def download_image(url, filename):
    """Скачивает изображение"""
    try:
        response = requests.get(url, stream=True, timeout=30)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return True
    except:
        return False
    return False

def create_meme(input_path, output_path, top_text="", bottom_text=""):
    """Создает мем с текстом сверху и снизу"""
    try:
        # Открываем изображение
        img = Image.open(input_path)
        draw = ImageDraw.Draw(img)
        
        # Пробуем загрузить жирный шрифт
        try:
            font = ImageFont.truetype("impact.ttf", 40)
        except:
            try:
                font = ImageFont.truetype("arialbd.ttf", 40)
            except:
                try:
                    font = ImageFont.truetype("DejaVuSans-Bold.ttf", 40)
                except:
                    font = ImageFont.load_default()
        
        # Функция для добавления текста с обводкой
        def draw_text_with_outline(text, y_position):
            if not text:
                return
            
            # Получаем размеры текста
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            x = (img.width - text_width) // 2
            
            # Черная обводка
            for offset_x in [-2, -1, 1, 2]:
                for offset_y in [-2, -1, 1, 2]:
                    draw.text((x + offset_x, y_position + offset_y), 
                             text, font=font, fill='black')
            
            # Белый текст
            draw.text((x, y_position), text, font=font, fill='white')
        
        # Верхний текст
        if top_text:
            draw_text_with_outline(top_text.upper(), 10)
        
        # Нижний текст
        if bottom_text:
            bbox = draw.textbbox((0, 0), bottom_text.upper(), font=font)
            text_height = bbox[3] - bbox[1]
            y_position = img.height - text_height - 10
            draw_text_with_outline(bottom_text.upper(), y_position)
        
        # Сохраняем
        img.save(output_path)
        return True
        
    except Exception as e:
        print(f"Ошибка создания мема: {e}")
        return False

def process(clean_command, vk, message_id, peer_id, user_id):
    """Обрабатывает .meme"""
    
    try:
        # Удаляем сообщение команды
        try:
            vk.messages.delete(message_ids=message_id, delete_for_all=1)
        except:
            pass
        
        # Парсим команду: .meme <верх>|<низ>
        parts = clean_command.split(maxsplit=1)
        if len(parts) < 2:
            return ""
        
        text = parts[1]
        if '|' in text:
            top_text, bottom_text = text.split('|', 1)
            top_text = top_text.strip()
            bottom_text = bottom_text.strip()
        else:
            top_text = text
            bottom_text = ""
        
        # Получаем сообщение
        messages = vk.messages.getById(message_ids=[message_id])
        if not messages['items']:
            return ""
        
        message = messages['items'][0]
        
        if 'reply_message' not in message:
            return ""
        
        reply_message = message['reply_message']
        reply_attachments = reply_message.get('attachments', [])
        
        # Ищем фотографии
        photo_attachments = []
        for att in reply_attachments:
            if att['type'] == 'photo':
                photo_attachments.append(att)
        
        if not photo_attachments:
            return ""
        
        # Берем первую фотографию
        photo_att = photo_attachments[0]
        att_info = get_attachment_info(photo_att)
        
        if 'url' not in att_info:
            return ""
        
        # Создаем временные файлы
        temp_dir = tempfile.gettempdir()
        timestamp = int(time.time())
        
        input_filename = os.path.join(temp_dir, f"photo_{timestamp}.jpg")
        output_filename = os.path.join(temp_dir, f"meme_{timestamp}.jpg")
        
        # Скачиваем фотографию
        if not download_image(att_info['url'], input_filename):
            return ""
        
        # Создаем мем
        if not create_meme(input_filename, output_filename, top_text, bottom_text):
            if os.path.exists(input_filename):
                try:
                    os.remove(input_filename)
                except:
                    pass
            return ""
        
        # Загружаем на сервер VK
        upload_server = vk.photos.getMessagesUploadServer(peer_id=peer_id)
        upload_url = upload_server['upload_url']
        
        with open(output_filename, 'rb') as f:
            files = {'photo': f}
            response = requests.post(upload_url, files=files, timeout=120)
            
            if response.status_code != 200:
                return ""
            
            result = response.json()
            
            if 'error' in result:
                return ""
            
            # Сохраняем фото
            save_result = vk.photos.saveMessagesPhoto(
                server=result['server'],
                photo=result['photo'],
                hash=result['hash']
            )
            
            if not save_result or len(save_result) == 0:
                return ""
            
            saved_photo = save_result[0]
            attachment = f"photo{saved_photo['owner_id']}_{saved_photo['id']}"
            
            # Отправляем мем
            vk.messages.send(
                peer_id=peer_id,
                attachment=attachment,
                random_id=0
            )
        
        # Удаляем временные файлы
        for f in [input_filename, output_filename]:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except:
                    pass
        
        return ""
        
    except Exception as e:
        print(f"Ошибка в .meme: {e}")
        return ""