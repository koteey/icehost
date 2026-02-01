"""
Команда .dist / .d - жмых изображений через Seam Carving с растягиванием
"""

import os
import tempfile
import time
import requests
import numpy as np
from PIL import Image, ImageFilter

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

def get_attachment_info(attachment):
    """Получает информацию о вложении"""
    att_type = attachment['type']
    
    if att_type == 'photo':
        photo = attachment['photo']
        sizes = photo.get('sizes', [])
        if sizes:
            for size_type in ['w', 'z', 'y', 'x', 'm', 's']:
                for size in sizes:
                    if size.get('type') == size_type:
                        return {
                            'type': 'photo',
                            'url': size['url'],
                            'width': size.get('width'),
                            'height': size.get('height')
                        }
    
    elif att_type == 'sticker':
        sticker = attachment['sticker']
        images = sticker.get('images', [])
        if images:
            for img in images:
                if img.get('url'):
                    return {
                        'type': 'sticker',
                        'url': img['url'],
                        'width': img.get('width'),
                        'height': img.get('height')
                    }
    
    return {'type': att_type}

def compute_energy(image_array):
    """
    Вычисляет карту энергии изображения
    """
    if len(image_array.shape) == 3:
        gray = np.mean(image_array, axis=2)
    else:
        gray = image_array
    
    dx = np.abs(np.gradient(gray, axis=1))
    dy = np.abs(np.gradient(gray, axis=0))
    
    energy = dx + dy
    
    # Увеличиваем энергию на краях для защиты от обрезания
    energy[:, 0] += 1000
    energy[:, -1] += 1000
    energy[0, :] += 1000
    energy[-1, :] += 1000
    
    return energy

def find_seam(energy):
    """
    Находит шов с минимальной энергией
    """
    h, w = energy.shape
    
    # Матрица накопленной энергии
    M = energy.copy()
    backtrack = np.zeros_like(M, dtype=np.int32)
    
    # Заполняем матрицу
    for i in range(1, h):
        for j in range(0, w):
            # Возможные предыдущие пиксели
            if j == 0:
                indices = [j, j + 1]
            elif j == w - 1:
                indices = [j - 1, j]
            else:
                indices = [j - 1, j, j + 1]
            
            # Находим минимальную энергию
            min_energy = M[i - 1, indices[0]]
            min_index = indices[0]
            
            for idx in indices[1:]:
                if M[i - 1, idx] < min_energy:
                    min_energy = M[i - 1, idx]
                    min_index = idx
            
            M[i, j] += min_energy
            backtrack[i, j] = min_index
    
    # Находим конечную точку шва
    j = np.argmin(M[-1])
    
    # Восстанавливаем шов
    seam = []
    for i in range(h - 1, -1, -1):
        seam.append(j)
        j = backtrack[i, j]
    
    seam.reverse()
    return seam

def remove_seam_horizontal(image_array, seam):
    """
    Удаляет горизонтальный шов из изображения
    """
    h, w = image_array.shape[:2]
    new_w = w - 1
    
    # Проверяем соответствие размеров
    if len(seam) != h:
        # Корректируем шов до нужного размера
        if len(seam) > h:
            seam = seam[:h]
        else:
            seam = seam + [seam[-1]] * (h - len(seam))
    
    # Создаем новое изображение без шва
    if len(image_array.shape) == 3:
        c = image_array.shape[2]
        new_image = np.zeros((h, new_w, c), dtype=image_array.dtype)
        
        for i in range(h):
            j_seam = seam[i] if i < len(seam) else seam[-1]
            j_seam = min(j_seam, w - 1)  # Защита от выхода за границы
            
            # Копируем левую часть
            if j_seam > 0:
                new_image[i, :j_seam] = image_array[i, :j_seam]
            
            # Копируем правую часть
            if j_seam < w - 1:
                new_image[i, j_seam:] = image_array[i, j_seam + 1:]
    else:
        new_image = np.zeros((h, new_w), dtype=image_array.dtype)
        
        for i in range(h):
            j_seam = seam[i] if i < len(seam) else seam[-1]
            j_seam = min(j_seam, w - 1)
            
            if j_seam > 0:
                new_image[i, :j_seam] = image_array[i, :j_seam]
            if j_seam < w - 1:
                new_image[i, j_seam:] = image_array[i, j_seam + 1:]
    
    return new_image

def remove_seam_vertical(image_array, seam):
    """
    Удаляет вертикальный шов из изображения
    """
    # Транспонируем, удаляем горизонтальный шов, транспонируем обратно
    if len(image_array.shape) == 3:
        transposed = np.transpose(image_array, (1, 0, 2))
    else:
        transposed = np.transpose(image_array)
    
    result = remove_seam_horizontal(transposed, seam)
    
    if len(image_array.shape) == 3:
        return np.transpose(result, (1, 0, 2))
    else:
        return np.transpose(result)

def seam_carve_and_stretch(image_array, reduction_percent, original_size):
    """
    Основная функция: делает жмых и растягивает обратно
    """
    h, w = image_array.shape[:2]
    orig_h, orig_w = original_size
    
    # Вычисляем целевой размер после жмыха
    target_w = max(10, int(w * (1 - reduction_percent / 100)))
    target_h = max(10, int(h * (1 - reduction_percent / 100)))
    
    result = image_array.copy()
    
    # ЖМЫХ: Удаляем швы до достижения целевого размера
    if w > target_w:
        for _ in range(w - target_w):
            energy = compute_energy(result)
            seam = find_seam(energy)
            
            # Проверяем длину шва
            if len(seam) != result.shape[0]:
                break
            
            result = remove_seam_horizontal(result, seam)
            
            # Если изображение стало слишком маленьким
            if result.shape[1] <= 10:
                break
    
    if h > target_h:
        for _ in range(h - target_h):
            energy = compute_energy(result)
            seam = find_seam(energy)
            
            # Проверяем длину шва
            if len(seam) != result.shape[1]:
                break
            
            result = remove_seam_vertical(result, seam)
            
            # Если изображение стало слишком маленьким
            if result.shape[0] <= 10:
                break
    
    # РАСТЯГИВАНИЕ: Растягиваем обратно до исходного размера
    from PIL import Image
    
    # Конвертируем в PIL Image
    if len(result.shape) == 3:
        img_pil = Image.fromarray(result.astype(np.uint8))
    else:
        # Если это grayscale, конвертируем в RGB
        img_pil = Image.fromarray(result.astype(np.uint8))
        img_pil = img_pil.convert('RGB')
    
    # Растягиваем до исходного размера
    stretched_img = img_pil.resize((orig_w, orig_h), Image.Resampling.NEAREST)
    
    # Добавляем немного размытия для сглаживания артефактов
    if reduction_percent > 30:
        stretched_img = stretched_img.filter(ImageFilter.GaussianBlur(radius=0.5))
    
    return np.array(stretched_img)

def fast_seam_carve_stretch(image_array, quality_level):
    """
    Быстрая версия с растягиванием
    quality_level: 1-10 (1 - максимальный жмых)
    """
    h, w = image_array.shape[:2]
    
    # Определяем процент уменьшения
    if quality_level <= 3:
        reduction = 70 + (3 - quality_level) * 10  # 70-90%
    elif quality_level <= 7:
        reduction = 40 + (7 - quality_level) * 10  # 40-70%
    else:
        reduction = 20 + (10 - quality_level) * 5  # 20-35%
    
    # Запоминаем исходный размер
    original_size = (h, w)
    
    # Ограничиваем максимальный процент
    reduction = min(reduction, 95)
    
    # Если изображение слишком большое, сначала уменьшим для скорости
    if w > 400 or h > 400:
        # Временно уменьшаем для скорости обработки
        scale_factor = 400 / max(w, h)
        small_w = int(w * scale_factor)
        small_h = int(h * scale_factor)
        
        from PIL import Image
        img_pil = Image.fromarray(image_array.astype(np.uint8))
        small_img = img_pil.resize((small_w, small_h), Image.Resampling.LANCZOS)
        small_array = np.array(small_img)
        
        # Применяем seam carving к уменьшенной версии
        result_small = seam_carve_and_stretch(small_array, reduction, (small_h, small_w))
        
        # Растягиваем обратно до исходного размера
        result_img = Image.fromarray(result_small.astype(np.uint8))
        result_img = result_img.resize((w, h), Image.Resampling.NEAREST)
        
        return np.array(result_img)
    else:
        # Для маленьких изображений - полная обработка
        return seam_carve_and_stretch(image_array, reduction, original_size)

def process(clean_command, vk, message_id, peer_id, user_id):
    """Обрабатывает команды .dist и .d с жмыхом и растягиванием"""
    
    try:
        # Удаляем сообщение с командой
        try:
            vk.messages.delete(message_ids=message_id, delete_for_all=1)
        except:
            pass
        
        messages = vk.messages.getById(message_ids=[message_id])
        if not messages['items']:
            return ""
        
        message = messages['items'][0]
        
        # Парсим аргументы
        parts = clean_command.split()
        quality_level = 5  # По умолчанию
        
        if len(parts) >= 2:
            try:
                level = int(parts[1])
                if 1 <= level <= 10:
                    quality_level = level
            except:
                pass
        
        # Ищем изображение
        image_attachments = []
        
        if 'attachments' in message:
            for att in message['attachments']:
                if att['type'] in ['photo', 'sticker']:
                    image_attachments.append(att)
        
        if 'reply_message' in message:
            reply_message = message['reply_message']
            if 'attachments' in reply_message:
                for att in reply_message['attachments']:
                    if att['type'] in ['photo', 'sticker']:
                        image_attachments.append(att)
        
        if not image_attachments:
            return ""
        
        # Берем первое изображение
        image_att = image_attachments[0]
        att_info = get_attachment_info(image_att)
        
        if 'url' not in att_info:
            return ""
        
        # Временные файлы
        temp_dir = tempfile.gettempdir()
        timestamp = int(time.time())
        
        ext = 'png' if att_info['type'] == 'sticker' else 'jpg'
        input_filename = os.path.join(temp_dir, f"input_{timestamp}.{ext}")
        output_filename = os.path.join(temp_dir, f"dist_stretch_{timestamp}.{ext}")
        
        # Скачиваем
        if not download_image(att_info['url'], input_filename):
            return ""
        
        # Открываем изображение
        try:
            img = Image.open(input_filename)
            
            # Конвертируем в RGB если нужно
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Конвертируем в numpy array
            img_array = np.array(img)
            
            # Применяем seam carving с растягиванием
            result_array = fast_seam_carve_stretch(img_array, quality_level)
            
            if result_array is None or result_array.size == 0:
                return ""
            
            # Конвертируем обратно в изображение
            result_img = Image.fromarray(result_array.astype(np.uint8))
            
            # Сохраняем
            if ext == 'png':
                result_img.save(output_filename, 'PNG', compress_level=1)
            else:
                result_img.save(output_filename, 'JPEG', quality=85, optimize=True)
            
        except:
            return ""
        
        # Загружаем на сервер VK
        if att_info['type'] == 'sticker':
            # Для стикеров - как граффити
            upload_server = vk.docs.getMessagesUploadServer(
                type='graffiti',
                peer_id=peer_id
            )
            upload_url = upload_server['upload_url']
            
            with open(output_filename, 'rb') as f:
                files = {'file': ('graffiti.png', f)}
                response = requests.post(upload_url, files=files, timeout=120)
                
                if response.status_code != 200:
                    return ""
                
                result = response.json()
                
                if 'error' in result or 'file' not in result:
                    return ""
                
                save_result = vk.docs.save(file=result['file'], title='graffiti.png')
                
                if not save_result:
                    return ""
                
                uploaded_doc = save_result['graffiti']
                attachment = f"graffiti{uploaded_doc['owner_id']}_{uploaded_doc['id']}"
        else:
            # Для фото
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
                
                save_result = vk.photos.saveMessagesPhoto(
                    server=result['server'],
                    photo=result['photo'],
                    hash=result['hash']
                )
                
                if not save_result or len(save_result) == 0:
                    return ""
                
                saved_photo = save_result[0]
                attachment = f"photo{saved_photo['owner_id']}_{saved_photo['id']}"
        
        # Отправляем результат
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