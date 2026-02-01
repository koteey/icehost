"""
Команды QR: .qr и .qrscan
"""

import os
import tempfile
import time
import requests
import qrcode
from PIL import Image
from lib.media_utils import get_attachment_info

def generate_qr(text):
    """Генерирует QR-код"""
    try:
        # Создаем QR-код
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)
        
        # Создаем изображение
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Сохраняем во временный файл
        temp_dir = tempfile.gettempdir()
        timestamp = int(time.time())
        filename = os.path.join(temp_dir, f"qr_{timestamp}.png")
        
        img.save(filename)
        return filename
        
    except Exception as e:
        print(f"Ошибка генерации QR: {e}")
        return None

def read_qr(image_path):
    """Читает QR-код с изображения"""
    try:
        # Для чтения QR нужна библиотека
        try:
            import pyzbar.pyzbar as pyzbar
        except ImportError:
            return "Установите библиотеку: pip install pyzbar"
        
        # Открываем изображение
        img = Image.open(image_path)
        
        # Декодируем QR
        decoded = pyzbar.decode(img)
        
        if decoded:
            return decoded[0].data.decode('utf-8')
        else:
            return "QR-код не найден"
            
    except Exception as e:
        print(f"Ошибка чтения QR: {e}")
        return f"Ошибка: {str(e)}"

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

def process_qr(clean_command, vk, message_id, peer_id, user_id):
    """Обрабатывает .qr"""
    
    try:
        # Удаляем сообщение команды
        try:
            vk.messages.delete(message_ids=message_id, delete_for_all=1)
        except:
            pass
        
        # Получаем текст для QR
        text = clean_command[3:].strip()  # Убираем ".qr "
        
        if not text:
            return ""
        
        # Генерируем QR-код
        qr_file = generate_qr(text)
        
        if not qr_file or not os.path.exists(qr_file):
            return ""
        
        # Загружаем как фото
        upload_server = vk.photos.getMessagesUploadServer(peer_id=peer_id)
        upload_url = upload_server['upload_url']
        
        with open(qr_file, 'rb') as f:
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
            
            # Отправляем QR-код
            vk.messages.send(
                peer_id=peer_id,
                attachment=attachment,
                message=f"📱 QR-код для: {text[:50]}...",
                random_id=0
            )
        
        # Удаляем временный файл
        if os.path.exists(qr_file):
            os.remove(qr_file)
        
        return ""
        
    except Exception as e:
        print(f"Ошибка в .qr: {e}")
        return ""

def process_qrscan(clean_command, vk, message_id, peer_id, user_id):
    """Обрабатывает .qrscan"""
    
    try:
        # Удаляем сообщение команды
        try:
            vk.messages.delete(message_ids=message_id, delete_for_all=1)
        except:
            pass
        
        # Получаем сообщение с фото
        messages = vk.messages.getById(message_ids=[message_id])
        if not messages['items']:
            return ""
        
        message = messages['items'][0]
        
        if 'reply_message' not in message:
            vk.messages.send(
                peer_id=peer_id,
                message="❌ Ответьте на сообщение с QR-кодом!",
                random_id=0
            )
            return ""
        
        reply_message = message['reply_message']
        reply_attachments = reply_message.get('attachments', [])
        
        # Ищем фотографии
        photo_attachments = []
        for att in reply_attachments:
            if att['type'] == 'photo':
                photo_attachments.append(att)
        
        if not photo_attachments:
            vk.messages.send(
                peer_id=peer_id,
                message="❌ В сообщении нет фото!",
                random_id=0
            )
            return ""
        
        # Берем первую фотографию
        photo_att = photo_attachments[0]
        att_info = get_attachment_info(photo_att)
        
        if 'url' not in att_info:
            return ""
        
        # Создаем временный файл
        temp_dir = tempfile.gettempdir()
        timestamp = int(time.time())
        input_filename = os.path.join(temp_dir, f"qr_scan_{timestamp}.jpg")
        
        # Скачиваем фотографию
        if not download_image(att_info['url'], input_filename):
            vk.messages.send(
                peer_id=peer_id,
                message="❌ Не удалось скачать фото!",
                random_id=0
            )
            return ""
        
        # Читаем QR-код
        result = read_qr(input_filename)
        
        # Удаляем временный файл
        if os.path.exists(input_filename):
            os.remove(input_filename)
        
        # Отправляем результат
        vk.messages.send(
            peer_id=peer_id,
            message=f"🔍 Результат сканирования:\n\n{result}",
            random_id=0
        )
        
        return ""
        
    except Exception as e:
        print(f"Ошибка в .qrscan: {e}")
        return ""