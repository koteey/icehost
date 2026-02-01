"""
Команда .demot - создает демотиватор из фотографии
"""

import os
import tempfile
import time
import requests

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

def create_demotivator(input_path, output_path, text, frame_color='black'):
    """
    Создает демотиватор из изображения
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Открываем изображение
        img = Image.open(input_path)
        
        # Размеры
        img_width, img_height = img.size
        border = 20
        frame_width = 10
        
        # Создаем новое изображение с рамкой
        new_width = img_width + 2 * border + 2 * frame_width
        new_height = img_height + 2 * border + 2 * frame_width + 100
        
        # Создаем фон
        if frame_color == 'black':
            background_color = (0, 0, 0)
        else:
            background_color = (255, 255, 255)
        
        result = Image.new('RGB', (new_width, new_height), background_color)
        
        # Вставляем изображение с рамкой
        # Сначала белая рамка
        white_border = Image.new('RGB', (img_width + 2 * frame_width, img_height + 2 * frame_width), (255, 255, 255))
        result.paste(white_border, (border, border))
        
        # Потом само изображение
        result.paste(img, (border + frame_width, border + frame_width))
        
        # Добавляем текст
        draw = ImageDraw.Draw(result)
        
        # Пробуем загрузить шрифт
        try:
            font_large = ImageFont.truetype("arial.ttf", 36)
            font_small = ImageFont.truetype("arial.ttf", 24)
        except:
            try:
                font_large = ImageFont.truetype("DejaVuSans.ttf", 36)
                font_small = ImageFont.truetype("DejaVuSans.ttf", 24)
            except:
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()
        
        # Текст демотиватора
        text_y = new_height - 80
        
        if frame_color == 'black':
            text_color = 'white'
        else:
            text_color = 'black'
        
        # Добавляем основную надпись
        bbox = draw.textbbox((0, 0), text, font=font_large)
        text_width = bbox[2] - bbox[0]
        x = (new_width - text_width) // 2
        
        # Обводка для читаемости
        for offset_x in [-1, 0, 1]:
            for offset_y in [-1, 0, 1]:
                if offset_x == 0 and offset_y == 0:
                    continue
                draw.text((x + offset_x, text_y + offset_y), text, font=font_large, fill='black')
        
        # Основной текст
        draw.text((x, text_y), text, font=font_large, fill=text_color)
        
        # Добавляем подпись
        signature = "lol kek chebyrek"
        bbox = draw.textbbox((0, 0), signature, font=font_small)
        text_width = bbox[2] - bbox[0]
        x = (new_width - text_width) // 2
        
        for offset_x in [-1, 0, 1]:
            for offset_y in [-1, 0, 1]:
                if offset_x == 0 and offset_y == 0:
                    continue
                draw.text((x + offset_x, text_y + 50 + offset_y), signature, font=font_small, fill='black')
        
        draw.text((x, text_y + 50), signature, font=font_small, fill=text_color)
        
        # Сохраняем
        result.save(output_path)
        return True
        
    except Exception as e:
        print(f"Ошибка создания демотиватора: {e}")
        return False

def get_attachment_info(attachment):
    """Получает информацию о вложении"""
    att_type = attachment['type']
    
    if att_type == 'photo':
        photo = attachment['photo']
        # Берем самую большую доступную фотографию
        sizes = photo.get('sizes', [])
        if sizes:
            # Ищем размер type='z' или 'y' или 'x' или 'm'
            for size_type in ['z', 'y', 'x', 'm', 's']:
                for size in sizes:
                    if size.get('type') == size_type:
                        return {
                            'type': 'photo',
                            'url': size['url'],
                            'width': size.get('width'),
                            'height': size.get('height')
                        }
    return {'type': att_type}

def process(clean_command, vk, message_id, peer_id, user_id):
    """Обрабатывает команду .demot"""
    
    # Парсим команду: .demot [текст]
    parts = clean_command.split(maxsplit=1)
    if len(parts) < 2:
        return ""
    
    text = parts[1]
    
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
        output_filename = os.path.join(temp_dir, f"demotivator_{timestamp}.jpg")
        
        # Скачиваем фотографию
        if not download_image(att_info['url'], input_filename):
            return ""
        
        # Создаем демотиватор
        if not create_demotivator(input_filename, output_filename, text):
            # Удаляем временные файлы
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
            
            # Отправляем демотиватор
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
        
    except:
        return ""