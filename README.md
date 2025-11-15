# Юзербот для vk.com IceHost
# Разработано командой SnowCode (@snowcoding)


# Установка:
1. Скачайте релизный архив.
2. Распакуйте в удобное вам место.
3. Установите зависимости: ```bash
pip install vk-api requests pillow numpy pandas beautifulsoup4 scikit-learn tensorflow plyer openpyxl```
4. В файле icehostdata.ini укажите токен авторизации из https://vkhost.github.io/ (выберите Kate Mobile), и ваш id.
5. Запустите.
6. Используйте.



# 📋 Доступные команды:
• .info - информация
• .ping - проверка сети
• .hotkey - создать хоткей
• .hotlist - список хоткеев
• .delhotkey - удалить хоткей
• .modules - список модулей
• .dm - установить модуль
• .delm имя - удалить модуль
• .settings - настройки
• .python код - выполнить код в python
• .terminal команда - выполнить команду в терминале

📋 Доп. Модули:
• .calc выражение - вычислить выражение
• .math - справка по калькулятору
• .config список - показать все модули и их настройки
• .config модули - показать только список модулей
• .config получить <модуль> - показать настройки модуля
• .config установить <модуль> <параметр> <значение> - изменить настройку
• .config сбросить <модуль> - сбросить настройки модуля
• .config создать <модуль> <параметр> <значение> - создать новую настройку
• .config удалить <модуль> <параметр> - удалить настройку




# 📖 Полное руководство по созданию модулей для IceHost

## 🎯 Основная структура модуля

Каждый модуль - это Python файл в папке `modules/` со следующей структурой:

### 📁 Базовый шаблон модуля

```python
MODULE_INFO = {
    'name': 'Название модуля',
    'version': '1.0',
    'description': 'Описание модуля',
    'author': 'Ваше имя'
}

MODULE_COMMANDS = [
    'команда1 описание - что делает команда1',
    'команда2 описание - что делает команда2'
]

def process_command(command, vk, peer_id, user_id, settings=None):
    """
    Основная функция обработки команд модуля
    """
    if command.startswith('команда1 '):
        # Обработка команды1
        return "Результат команды1"
    
    elif command == 'команда2':
        # Обработка команды2
        return "Результат команды2"
    
    # Если команда не обработана
    return None
```

## 🔧 Детальное описание компонентов

### 1. `MODULE_INFO` - информация о модуле
**Обязательные поля:**
```python
MODULE_INFO = {
    'name': 'Calculator',           # Название модуля
    'version': '1.0',               # Версия модуля
    'description': 'Математический калькулятор',  # Описание
    'author': 'YourName',           # Автор модуля
    # Дополнительные поля (опционально):
    'website': 'https://example.com',  # Сайт автора
    'dependencies': ['requests'],   # Зависимости
    'permissions': ['messages']     # Требуемые разрешения
}
```

### 2. `MODULE_COMMANDS` - список команд
```python
MODULE_COMMANDS = [
    'calc выражение - вычисляет математическое выражение',
    'math помощь - показывает справку',
    'config настройки - управление настройками модуля'
]
```

### 3. `process_command()` - главная функция
**Параметры:**
- `command` - текст команды (без префикса)
- `vk` - объект VK API
- `peer_id` - ID диалога
- `user_id` - ID пользователя
- `settings` - настройки бота (опционально)

**Возвращает:**
- `str` - текст для отправки
- `None` - если команда не для этого модуля

## 🚀 Примеры модулей

### 📊 Пример 1: Простой модуль-приветствие

```python
MODULE_INFO = {
    'name': 'Greeter',
    'version': '1.0',
    'description': 'Модуль приветствий и простых ответов',
    'author': 'SnowCode'
}

MODULE_COMMANDS = [
    'привет - поздороваться с ботом',
    'время - показать текущее время',
    'случайное число - сгенерировать случайное число'
]

def process_command(command, vk, peer_id, user_id, settings=None):
    import random
    import datetime
    
    if command == 'привет':
        return f"👋 Привет! Рад тебя видеть!\nТвой ID: {user_id}"
    
    elif command == 'время':
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        return f"🕐 Текущее время: {current_time}"
    
    elif command == 'случайное число':
        number = random.randint(1, 100)
        return f"🎲 Случайное число: {number}"
    
    return None
```

### 🧮 Пример 2: Калькулятор с настройками

```python
MODULE_INFO = {
    'name': 'Calculator',
    'version': '2.0',
    'description': 'Продвинутый калькулятор с настройками точности',
    'author': 'SnowCode'
}

MODULE_COMMANDS = [
    'calc выражение - вычислить математическое выражение',
    'calc настройки - показать текущие настройки',
    'math справка - подробная справка по калькулятору'
]

def get_calc_settings(settings):
    """Получает настройки калькулятора"""
    module_settings = settings.get('modules', {}).get('calculator', {}) if settings else {}
    return {
        'precision': module_settings.get('precision', 2),
        'show_steps': module_settings.get('show_steps', False),
        'angle_unit': module_settings.get('angle_unit', 'degrees')
    }

def process_command(command, vk, peer_id, user_id, settings=None):
    calc_settings = get_calc_settings(settings)
    precision = calc_settings['precision']
    
    if command.startswith('calc '):
        expression = command[5:].strip()
        
        if expression == 'настройки':
            return show_calc_settings(calc_settings)
        
        try:
            # Безопасное вычисление
            allowed_chars = set('0123456789+-*/.() ')
            if all(c in allowed_chars for c in expression):
                result = eval(expression)
                
                if isinstance(result, float):
                    result = round(result, precision)
                
                response = f"🧮 **Результат:**\n"
                response += f"• Выражение: `{expression}`\n"
                response += f"• Ответ: `{result}`\n"
                response += f"• Точность: {precision} знака\n"
                
                return response
            else:
                return "❌ Ошибка: Недопустимые символы"
                
        except ZeroDivisionError:
            return "❌ Ошибка: Деление на ноль"
        except Exception as e:
            return f"❌ Ошибка вычисления: {str(e)}"
    
    elif command == 'math справка':
        return show_calc_help(calc_settings)
    
    return None

def show_calc_settings(settings):
    """Показывает текущие настройки калькулятора"""
    return f"""
⚙️ **Настройки калькулятора:**

• Точность: {settings['precision']} знака
• Показ шагов: {'✅' if settings['show_steps'] else '❌'}
• Единицы углов: {settings['angle_unit']}

💡 Для изменения используйте:
`.config установить calculator precision 4`
`.config установить calculator show_steps true`
"""

def show_calc_help(settings):
    """Показывает справку по калькулятору"""
    return f"""
🧮 **Калькулятор - справка**

**Основные операции:**
• Сложение: `calc 5+3`
• Вычитание: `calc 10-4`
• Умножение: `calc 6*7`
• Деление: `calc 15/3`
• Скобки: `calc (2+3)*4`

**Примеры:**
• `calc 2+2*2` = 6
• `calc (2+2)*2` = 8
• `calc 10/3` = 3.33

**Текущая точность:** {settings['precision']} знака
"""
```

### 🌐 Пример 3: Модуль для работы с интернетом

```python
MODULE_INFO = {
    'name': 'Internet Tools',
    'version': '1.0',
    'description': 'Инструменты для работы с интернетом',
    'author': 'SnowCode',
    'dependencies': ['requests']
}

MODULE_COMMANDS = [
    'ping сайт - проверить доступность сайта',
    'ip информация - показать IP информацию',
    'погода город - узнать погоду'
]

def process_command(command, vk, peer_id, user_id, settings=None):
    import requests
    import socket
    
    if command.startswith('ping '):
        website = command[5:].strip()
        return ping_website(website)
    
    elif command == 'ip информация':
        return get_ip_info()
    
    elif command.startswith('погода '):
        city = command[7:].strip()
        return get_weather(city)
    
    return None

def ping_website(website):
    """Проверяет доступность сайта"""
    try:
        if not website.startswith(('http://', 'https://')):
            website = 'https://' + website
        
        response = requests.get(website, timeout=10)
        
        if response.status_code == 200:
            return f"✅ Сайт {website} доступен\n⏱️ Ответ: {response.elapsed.total_seconds():.2f}с"
        else:
            return f"⚠️ Сайт {website} отвечает с кодом {response.status_code}"
            
    except requests.exceptions.RequestException as e:
        return f"❌ Ошибка подключения к {website}: {str(e)}"

def get_ip_info():
    """Получает информацию о IP"""
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        # Получаем внешний IP
        external_ip = requests.get('https://api.ipify.org', timeout=5).text
        
        return f"🌐 **IP информация:**\n• Локальный IP: `{local_ip}`\n• Внешний IP: `{external_ip}`\n• Имя хоста: `{hostname}`"
        
    except Exception as e:
        return f"❌ Ошибка получения IP информации: {str(e)}"

def get_weather(city):
    """Получает погоду для города"""
    try:
        # Здесь можно подключить любой weather API
        # Например, OpenWeatherMap
        return f"🌤️ Функция погоды для {city} в разработке..."
        
    except Exception as e:
        return f"❌ Ошибка получения погоды: {str(e)}"
```

## ⚙️ Работа с настройками модуля

### 📋 Получение настроек
```python
def get_module_settings(settings, module_name):
    """Безопасное получение настроек модуля"""
    if settings and 'modules' in settings and module_name in settings['modules']:
        return settings['modules'][module_name]
    return {}

# Использование:
module_settings = get_module_settings(settings, 'calculator')
precision = module_settings.get('precision', 2)
theme = module_settings.get('theme', 'default')
```

### 🎛️ Пример модуля с настройками

```python
MODULE_INFO = {
    'name': 'Configurable Module',
    'version': '1.0',
    'description': 'Модуль с настраиваемыми параметрами',
    'author': 'SnowCode'
}

MODULE_COMMANDS = [
    'test - тестовая команда',
    'config - показать настройки'
]

def process_command(command, vk, peer_id, user_id, settings=None):
    # Получаем настройки модуля
    module_settings = get_module_settings(settings, 'configurable_module')
    
    if command == 'test':
        color = module_settings.get('color', 'синий')
        size = module_settings.get('size', 'medium')
        enabled = module_settings.get('enabled', True)
        
        return f"🎨 Тест модуля:\n• Цвет: {color}\n• Размер: {size}\n• Включен: {'✅' if enabled else '❌'}"
    
    elif command == 'config':
        return show_module_config(module_settings)
    
    return None

def get_module_settings(settings, module_name):
    """Безопасное получение настроек модуля"""
    if settings and 'modules' in settings and module_name in settings['modules']:
        return settings['modules'][module_name]
    return {}

def show_module_config(settings):
    """Показывает конфигурацию модуля"""
    config_text = "⚙️ **Настройки модуля:**\n"
    
    if settings:
        for key, value in settings.items():
            config_text += f"• {key}: `{value}`\n"
    else:
        config_text += "⚠️ Настроек нет\n"
    
    config_text += "\n💡 **Команды управления:**\n"
    config_text += "`.config установить configurable_module color red`\n"
    config_text += "`.config установить configurable_module size large`\n"
    config_text += "`.config установить configurable_module enabled false`"
    
    return config_text
```

## 🔧 Работа с VK API

### 💬 Отправка сообщений
```python
def process_command(command, vk, peer_id, user_id, settings=None):
    if command == 'отправить тест':
        try:
            # Отправка сообщения через VK API
            vk.messages.send(
                peer_id=peer_id,
                message="📨 Это тестовое сообщение!",
                random_id=0
            )
            return "✅ Сообщение отправлено!"
        except Exception as e:
            return f"❌ Ошибка отправки: {str(e)}"
```

### 👤 Получение информации о пользователе
```python
def get_user_info(vk, user_id):
    """Получает информацию о пользователе"""
    try:
        user_info = vk.users.get(user_ids=user_id, fields='first_name,last_name,online')[0]
        return user_info
    except Exception as e:
        return None

def process_command(command, vk, peer_id, user_id, settings=None):
    if command == 'моя информация':
        user_info = get_user_info(vk, user_id)
        if user_info:
            return f"👤 **Ваш профиль:**\n• Имя: {user_info['first_name']}\n• Фамилия: {user_info['last_name']}\n• Онлайн: {'✅' if user_info.get('online') else '❌'}"
        else:
            return "❌ Не удалось получить информацию"
```

## 🛠️ Лучшие практики

### 1. **Обработка ошибок**
```python
def process_command(command, vk, peer_id, user_id, settings=None):
    try:
        # Ваш код здесь
        if command == 'тест':
            return "✅ Успех!"
        
        return None
    except Exception as e:
        return f"❌ Ошибка в модуле: {str(e)}"
```

### 2. **Валидация входных данных**
```python
def safe_eval(expression):
    """Безопасное вычисление выражений"""
    allowed_chars = set('0123456789+-*/.() ')
    return all(c in allowed_chars for c in expression)

def process_command(command, vk, peer_id, user_id, settings=None):
    if command.startswith('calc '):
        expression = command[5:].strip()
        
        if not safe_eval(expression):
            return "❌ Ошибка: Недопустимые символы в выражении"
        
        # Дальнейшая обработка...
```

### 3. **Логирование**
```python
import logging

def process_command(command, vk, peer_id, user_id, settings=None):
    print(f"[Модуль] Команда: {command} от {user_id}")
    # Обработка команды...
```

## 📦 Установка модуля

1. **Создайте файл** в папке `modules/your_module.py`
2. **Напишите код** по шаблону выше
3. **Отправьте файл** в диалог с ботом
4. **Установите командой:** `.dm` (ответом на файл)

## 🎉 Поздравляю!

Теперь вы знаете как создавать модули для IceHost. Начните с простых модулей и постепенно переходите к более сложным! 

**Полезные команды для тестирования:**
- `.modules` - список установленных модулей
- `.config список` - все настройки модулей
- `.delm имя_модуля` - удалить модуль


Удачи в создании модулей! 🚀



