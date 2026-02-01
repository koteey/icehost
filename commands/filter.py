"""
Команда .filter - фильтры для фото
"""

import os
import tempfile
import time
import requests
from PIL import Image, ImageFilter, ImageOps
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

def apply_filter(input_path, output_path, filter_name):
    """Применяет фильтр к изображению"""
    try:
        img = Image.open(input_path)
        
        if filter_name in ['grayscale', 'gray', 'grey']:
            img = ImageOps.grayscale(img)
        
        elif filter_name in ['sepia', 'sepia']:
            # Сепия эффект
            width, height = img.size
            pixels = img.load()
            
            for py in range(height):
                for px in range(width):
                    r, g, b = img.getpixel((px, py))
                    
                    # Формула сепии
                    tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                    tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                    tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                    
                    pixels[px, py] = (
                        min(255, tr),
                        min(255, tg),
                        min(255, tb)
                    )
        
        elif filter_name in ['blur', 'размытие']:
            img = img.filter(ImageFilter.GaussianBlur(radius=2))
        
        elif filter_name in ['sharpen', 'резкость']:
            img = img.filter(ImageFilter.SHARPEN)
        
        elif filter_name in ['edge', 'края']:
            img = img.filter(ImageFilter.FIND_EDGES)
        
        elif filter_name in ['invert', 'инверсия']:
            if img.mode == 'RGBA':
                r, g, b, a = img.split()
                rgb = Image.merge('RGB', (r, g, b))
                inverted = ImageOps.invert(rgb)
                r2, g2, b2 = inverted.split()
                img = Image.merge('RGBA', (r2, g2, b2, a))
            else:
                img = ImageOps.invert(img)
        
        elif filter_name in ['posterize', 'постеризация']:
            img = ImageOps.posterize(img, 3)
        
        elif filter_name in ['solarize', 'соляризация']:
            img = ImageOps.solarize(img, threshold=128)
        
        else:
            return False
        
        img.save(output_path)
        return True
        
    except Exception as e:
        print(f"Ошибка фильтра: {e}")
        return False

def process(clean_command, vk, message_id, peer_id, user_id):
    """Обрабатывает .filter"""
    
    try:
        # Удаляем сообщение команды
        try:
            vk.messages.delete(message_ids=message_id, delete_for_all=1)
        except:
            pass
        
        # Парсим команду: .filter <название>
        parts = clean_command.split()
        if len(parts) < 2:
            return ""
        
        filter_name = parts[1].lower()
        
        # Доступные фильтры
        filters = {
            'grayscale': 'чёрно-белый',
            'gray': 'чёрно-белый',
            'grey': 'чёрно-белый',
            'sepia': 'сепия',
            'blur': 'размытие',
            'sharpen': 'резкость',
            'edge': 'края',
            'invert': 'инверсия',
            'posterize': 'постеризация',
            'solarize': 'соляризация'
        }
        
        if filter_name not in filters:
            return ""
        
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
        output_filename = os.path.join(temp_dir, f"filter_{timestamp}.jpg")
        
        # Скачиваем фотографию
        if not download_image(att_info['url'], input_filename):
            return ""
        
        # Применяем фильтр
        if not apply_filter(input_filename, output_filename, filter_name):
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
            
            # Отправляем фото с фильтром
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
        print(f"Ошибка в .filter: {e}")
        return ""