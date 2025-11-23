# Юзербот для vk.com IceHost
# Разработано командой SnowCode (@snowcoding)


# Установка:
1. Скачайте релизный архив.
2. Распакуйте в удобное вам место.
3. Установите зависимости: ```pip install vk-api requests```
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




# 🚀 IceHost Modules v2.0 - Полное руководство по созданию модулей

## 📖 Оглавление
- [Новые возможности](#-новые-возможности)
- [Структура модуля](#-структура-модуля)
- [Типы обработчиков](#-типы-обработчиков)
- [Примеры модулей](#-примеры-модулей)
- [Утилиты и хелперы](#-утилиты-и-хелперы)
- [Лучшие практики](#-лучшие-практики)

## 🆕 Новые возможности

### 🔥 Обработка всех сообщений
Модули теперь могут обрабатывать ЛЮБЫЕ сообщения, даже без префикса команды!

### 👥 Реакция на сообщения других пользователей
Модули могут реагировать на сообщения от любого пользователя в беседе.

### 🔄 Обработка ответов
Модули могут обрабатывать ответы на сообщения, включая вложения и файлы.

### 📡 Обработка событий VK
Модули могут реагировать на любые события LongPoll (онлайн, редактирование сообщений и т.д.)

### ⚡ Перехват команд
Модули могут перехватывать команды до основной обработки.

## 📋 Структура модуля

### Базовый шаблон
```python
MODULE_INFO = {
    'name': 'Название модуля',
    'version': '1.0',
    'description': 'Описание модуля',
    'author': 'Ваше имя'
}

MODULE_COMMANDS = [
    'команда описание - что делает команда'
]

def process_command(command, vk, peer_id, user_id, settings=None):
    """Обработка команд с префиксом"""
    if command == 'команда':
        return "Результат команды"
    return None

# 🔥 НОВЫЕ ОБРАБОТЧИКИ (опционально)
def on_message_received(message_text, vk, peer_id, message_id, from_user_id, user_id, settings):
    """Обработка ВСЕХ сообщений (даже без префикса)"""
    return None  # Возвращает None или измененный текст

def on_any_message(message_text, vk, peer_id, message_id, from_user_id, user_id, settings):
    """Обработка сообщений от ЛЮБОГО пользователя"""
    return None

def on_reply_received(original_message_text, reply_text, vk, peer_id, message_id, from_user_id, replied_user_id, replied_message_id, attachments, user_id, settings):
    """Обработка ответов на сообщения"""
    return None

def on_event(event_type, event_data, vk, user_id, settings):
    """Обработка событий VK"""
    return None

def on_command_intercept(command, vk, peer_id, message_id, user_id, settings):
    """Перехват команд до обработки"""
    return None
```

## 🎯 Типы обработчиков

### 1. `process_command()` - Основная команда
```python
def process_command(command, vk, peer_id, user_id, settings=None):
    # command - текст команды без префикса
    # vk - объект VK API
    # peer_id - ID диалога
    # user_id - ID пользователя
    # settings - настройки бота
    if command == 'test':
        return "✅ Тест выполнен!"
    return None
```

### 2. `on_message_received()` - Все сообщения
```python
def on_message_received(message_text, vk, peer_id, message_id, from_user_id, user_id, settings):
    # Обрабатывает ЛЮБОЕ сообщение
    if "привет" in message_text.lower():
        vk.messages.send(peer_id=peer_id, message="И тебе привет!", random_id=0)
    return None  # Не изменяем сообщение
```

### 3. `on_any_message()` - Сообщения других пользователей
```python
def on_any_message(message_text, vk, peer_id, message_id, from_user_id, user_id, settings):
    # Обрабатывает сообщения от ЛЮБОГО пользователя
    if from_user_id != user_id:  # Только не от владельца
        if "бот" in message_text.lower():
            vk.messages.send(peer_id=peer_id, message="Я здесь! 🎯", random_id=0)
    return None
```

### 4. `on_reply_received()` - Ответы на сообщения
```python
def on_reply_received(original_message_text, reply_text, vk, peer_id, message_id, from_user_id, replied_user_id, replied_message_id, attachments, user_id, settings):
    # Обрабатывает ответы
    if original_message_text == ".dm":
        # Ответ на команду установки модуля
        for attachment in attachments:
            if attachment['type'] == 'doc' and attachment['doc']['ext'] == 'py':
                return "📦 Обнаружен файл модуля!"
    return None
```

### 5. `on_event()` - События VK
```python
from vk_api.longpoll import VkEventType

def on_event(event_type, event_data, vk, user_id, settings):
    # Обрабатывает события LongPoll
    if event_type == VkEventType.USER_ONLINE:
        user_id = event_data['user_id']
        vk.messages.send(peer_id=user_id, message="Привет! Вижу ты онлайн 🌟", random_id=0)
    return None
```

### 6. `on_command_intercept()` - Перехват команд
```python
def on_command_intercept(command, vk, peer_id, message_id, user_id, settings):
    # Перехватывает команды до основной обработки
    if command == 'secret':
        return "🔒 Эта команда перехвачена!"
    return None  # Позволяет продолжить обычную обработку
```

## 💡 Примеры модулей

### Пример 1: Модуль авто-ответов
```python
MODULE_INFO = {
    'name': 'Auto Responder',
    'version': '1.0',
    'description': 'Автоматические ответы на сообщения',
    'author': 'IceHost Team'
}

MODULE_COMMANDS = [
    'ar список - показать авто-ответы',
    'ar добавить <триггер> <ответ> - добавить авто-ответ'
]

auto_responses = {
    'привет': 'И тебе привет! 👋',
    'как дела': 'Отлично! А у тебя? 😊',
    'пока': 'До встречи! 👋'
}

def on_any_message(message_text, vk, peer_id, message_id, from_user_id, user_id, settings):
    # Авто-ответы на сообщения
    message_lower = message_text.lower()
    for trigger, response in auto_responses.items():
        if trigger in message_lower:
            vk.messages.send(peer_id=peer_id, message=response, random_id=0)
            break
    return None

def process_command(command, vk, peer_id, user_id, settings=None):
    if command == 'ar список':
        response = "📋 Авто-ответы:\n" + "\n".join([f"• {k} → {v}" for k, v in auto_responses.items()])
        return response
    return None
```

### Пример 2: Модуль модерации
```python
MODULE_INFO = {
    'name': 'Chat Moderator',
    'version': '1.0', 
    'description': 'Модерация чата и фильтрация контента',
    'author': 'IceHost Team'
}

banned_words = ['спам', 'оскорбление', 'реклама']

def on_any_message(message_text, vk, peer_id, message_id, from_user_id, user_id, settings):
    # Фильтрация запрещенных слов
    for word in banned_words:
        if word in message_text.lower():
            try:
                # Удаляем сообщение
                vk.messages.delete(
                    peer_id=peer_id,
                    message_ids=message_id,
                    delete_for_all=1
                )
                # Предупреждение пользователю
                vk.messages.send(
                    peer_id=peer_id,
                    message=f"⚠️ Сообщение удалено. Не используйте запрещенные слова.",
                    random_id=0
                )
            except:
                pass
            break
    return None
```

### Пример 3: Модуль уведомлений
```python
MODULE_INFO = {
    'name': 'Notifier',
    'version': '1.0',
    'description': 'Уведомления о событиях',
    'author': 'IceHost Team'
}

def on_event(event_type, event_data, vk, user_id, settings):
    # Уведомления о событиях
    if event_type == VkEventType.USER_ONLINE:
        user_info = vk.users.get(user_ids=[event_data['user_id']])[0]
        user_name = f"{user_info['first_name']} {user_info['last_name']}"
        
        vk.messages.send(
            peer_id=user_id,  # Лично владельцу
            message=f"👤 {user_name} сейчас онлайн!",
            random_id=0
        )
    
    elif event_type == VkEventType.MESSAGE_EDIT:
        vk.messages.send(
            peer_id=user_id,
            message=f"✏️ Сообщение отредактировано в беседе {event_data['peer_id']}",
            random_id=0
        )
    
    return None
```

## 🛠️ Утилиты и хелперы

### Доступ к утилитам бота
```python
def process_command(command, vk, peer_id, user_id, settings=None):
    # Доступ к утилитам через settings
    utils = settings.get('_utils', {})
    
    uptime = utils.get('get_uptime', lambda: "Недоступно")()
    latency = utils.get('measure_network_latency', lambda vk: "Недоступно")(vk)
    
    return f"⏱️ Аптайм: {uptime}\n🌐 Пинг: {latency:.2f}ms"
```

### Доступные утилиты:
- `get_uptime()` - время работы бота
- `measure_network_latency(vk)` - задержка до API VK  
- `get_connection_quality(latency)` - качество соединения
- `get_message_sender(vk, peer_id, message_id, user_id)` - определение отправителя
- `download_file(url, filename)` - скачивание файлов
- `save_settings(settings)` - сохранение настроек
- `load_settings()` - загрузка настроек
- `module_log(module_name, message)` - логирование

### Логирование для модулей
```python
def process_command(command, vk, peer_id, user_id, settings=None):
    utils = settings.get('_utils', {})
    log = utils.get('module_log', print)
    
    log("MyModule", f"Выполнена команда: {command}")
    return "Команда выполнена!"
```

## ✅ Лучшие практики

### 1. Обработка ошибок
```python
def process_command(command, vk, peer_id, user_id, settings=None):
    try:
        # Ваш код
        return "✅ Успех!"
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"
```

### 2. Проверка прав доступа
```python
def on_any_message(message_text, vk, peer_id, message_id, from_user_id, user_id, settings):
    # Только для владельца бота
    if from_user_id != user_id:
        return None
    
    # Ваш код для владельца
    return None
```

### 3. Использование настроек
```python
def process_command(command, vk, peer_id, user_id, settings=None):
    # Получение настроек модуля
    module_settings = settings.get('modules', {}).get('my_module', {})
    option = module_settings.get('option', 'значение по умолчанию')
    
    return f"Настройка: {option}"
```

### 4. Совместимость версий
```python
# Поддержка старых версий
def on_message_received(message_text, vk, peer_id, message_id, from_user_id, user_id, settings):
    # Работает с разным количеством аргументов
    return None

# Или минимальная версия
def on_message_received(message_text, vk, peer_id, user_id):
    # Только основные параметры
    return None
```

## 🚀 Установка модулей

1. Создайте файл в папке `modules/your_module.py`
2. Напишите код по шаблону выше
или:
1. Отправьте файл в диалог с ботом
2. Установите командой: `.dm` (ответом на файл)

## 📚 Полезные команды

- `.modules` - список установленных модулей
- `.config получить имя_модуля` - настройки модуля
- `.config установить имя_модуля параметр значение` - изменить настройки
- `.delm имя_модуля` - удалить модуль

---

**IceHost Modules v2.0** открывает безграничные возможности для создания интеллектуальных и интерактивных модулей! 🎉

*Создавайте, экспериментируйте, делитесь своими модулями с сообществом!* 🌟






