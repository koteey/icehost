"""
Утилиты для работы с изображениями
"""

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
import os
import tempfile
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
        pass
    return False

def invert_image(input_path, output_path):
    """Инвертирует цвета изображения"""
    try:
        img = Image.open(input_path)
        inverted = ImageOps.invert(img.convert('RGB'))
        inverted.save(output_path)
        return True
    except:
        return False

def add_text_to_image(input_path, output_path, text, position='top', font_size=40):
    """
    Добавляет текст на изображение
    
    Args:
        input_path: путь к входному изображению
        output_path: путь для сохранения
        text: текст для добавления
        position: 'top' или 'bottom'
        font_size: размер шрифта
    """
    try:
        # Открываем изображение
        img = Image.open(input_path)
        draw = ImageDraw.Draw(img)
        
        # Пробуем загрузить шрифт, иначе используем стандартный
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("DejaVuSans.ttf", font_size)
            except:
                font = ImageFont.load_default()
        
        # Вычисляем размеры текста
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Вычисляем позицию
        img_width, img_height = img.size
        
        if position == 'top':
            x = (img_width - text_width) // 2
            y = 20
        else:  # bottom
            x = (img_width - text_width) // 2
            y = img_height - text_height - 20
        
        # Рисуем черную обводку
        for offset_x in [-2, 0, 2]:
            for offset_y in [-2, 0, 2]:
                if offset_x == 0 and offset_y == 0:
                    continue
                draw.text((x + offset_x, y + offset_y), text, font=font, fill='black')
        
        # Рисуем белый текст поверх
        draw.text((x, y), text, font=font, fill='white')
        
        # Сохраняем
        img.save(output_path)
        return True
        
    except Exception as e:
        print(f"Ошибка добавления текста: {e}")
        return False

def create_demotivator(input_path, output_path, text, frame_color='black'):
    """
    Создает демотиватор из изображения
    
    Args:
        input_path: путь к входному изображению
        output_path: путь для сохранения
        text: текст для демотиватора
        frame_color: цвет рамки
    """
    try:
        # Открываем изображение
        img = Image.open(input_path)
        
        # Размеры
        img_width, img_height = img.size
        border = 20
        frame_width = 10
        
        # Создаем новое изображение с рамкой
        new_width = img_width + 2 * border + 2 * frame_width
        new_height = img_height + 2 * border + 2 * frame_width + 100  # Место для текста
        
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