"""
Команды рандомайзеров: .random, .dice, .coin, .chance, .kto, .vos
"""

import random
import re

def process_random(clean_command, vk, message_id, peer_id, user_id):
    """Обрабатывает .random <список>"""
    
    try:
        # Удаляем сообщение команды
        try:
            vk.messages.delete(message_ids=message_id, delete_for_all=1)
        except:
            pass
        
        # Получаем список
        text = clean_command[7:].strip()  # Убираем ".random "
        
        if not text:
            return ""
        
        # Разделяем по запятым или пробелам
        items = []
        if ',' in text:
            items = [item.strip() for item in text.split(',')]
        else:
            items = [item.strip() for item in text.split() if item.strip()]
        
        if len(items) < 2:
            return ""
        
        # Выбираем случайный элемент
        selected = random.choice(items)
        
        vk.messages.send(
            peer_id=peer_id,
            message=f"🎲 Случайный выбор: {selected}",  # Убрано форматирование **
            random_id=0
        )
        
        return ""
        
    except Exception as e:
        print(f"Ошибка в .random: {e}")
        return ""

def process_dice(clean_command, vk, message_id, peer_id, user_id):
    """Обрабатывает .dice"""
    
    try:
        # Удаляем сообщение команды
        try:
            vk.messages.delete(message_ids=message_id, delete_for_all=1)
        except:
            pass
        
        # Бросаем кубик
        result = random.randint(1, 6)
        
        # Эмодзи для кубика
        dice_emoji = {
            1: "⚀",
            2: "⚁", 
            3: "⚂",
            4: "⚃",
            5: "⚄",
            6: "⚅"
        }
        
        vk.messages.send(
            peer_id=peer_id,
            message=f"🎲 Выпало: {dice_emoji.get(result, result)} ({result})",
            random_id=0
        )
        
        return ""
        
    except Exception as e:
        print(f"Ошибка в .dice: {e}")
        return ""

def process_coin(clean_command, vk, message_id, peer_id, user_id):
    """Обрабатывает .coin"""
    
    try:
        # Удаляем сообщение команды
        try:
            vk.messages.delete(message_ids=message_id, delete_for_all=1)
        except:
            pass
        
        # Подбрасываем монетку
        vari = random.choice([1, 2])
        result = "орел" if vari == 2 else "решка" if vari == 1 else "монетка упала"
        emoji = "🦅" if result == "орел" else "💰" if result == "решка" else "❌"
        text = "Выпало:" if vari in [1, 2] else "Неудача,"
        
        vk.messages.send(
            peer_id=peer_id,
            message=f"{emoji} {text} {result}",
            random_id=0
        )
        
        return ""
        
    except Exception as e:
        print(f"Ошибка в .coin: {e}")
        return ""

def process_chance(clean_command, vk, message_id, peer_id, user_id):
    """Обрабатывает .chance <событие>"""
    
    try:
        # Удаляем сообщение команды
        try:
            vk.messages.delete(message_ids=message_id, delete_for_all=1)
        except:
            pass
        
        # Получаем событие
        event = clean_command[8:].strip()  # Убираем ".chance "
        
        if not event:
            return ""
        
        # Генерируем случайный процент
        chance = random.randint(0, 100)
        
        # Определяем эмодзи в зависимости от шанса
        if chance == 0:
            emoji = "💀"
        elif chance < 20:
            emoji = "📉"
        elif chance < 50:
            emoji = "🤔"
        elif chance < 80:
            emoji = "📈"
        elif chance < 100:
            emoji = "🔥"
        else:  # 100%
            emoji = "✅"
        
        vk.messages.send(
            peer_id=peer_id,
            message=f"{emoji} Шанс того что {event}: {chance}%",
            random_id=0
        )
        
        return ""
        
    except Exception as e:
        print(f"Ошибка в .chance: {e}")
        return ""

def process_kto(clean_command, vk, message_id, peer_id, user_id):
    """Обрабатывает .kto <вопрос>"""
    
    try:
        # Удаляем сообщение команды
        try:
            vk.messages.delete(message_ids=message_id, delete_for_all=1)
        except:
            pass
        
        # Получаем вопрос - исправлено: берем всю строку после команды
        command_parts = clean_command.split(' ', 1)
        question = command_parts[1] if len(command_parts) > 1 else ""
        
        # Получаем список пользователей в беседе
        try:
            if peer_id > 2000000000:  # Беседа
                members = vk.messages.getConversationMembers(peer_id=peer_id)
                users = []
                
                for item in members.get('items', []):
                    if 'member_id' in item:
                        member_id = item['member_id']
                        if member_id > 0:  # Не групповой чат
                            user_info = vk.users.get(user_ids=member_id)[0]
                            users.append(f"{user_info['first_name']} {user_info['last_name']}")
                
                if not users:
                    # Если не удалось получить участников, используем заготовленные имена
                    users = ["Анна", "Максим", "Дмитрий", "Екатерина", "Иван", "Ольга", 
                            "Сергей", "Мария", "Алексей", "Наталья"]
            
            else:  # Личные сообщения
                # В ЛС используем участников диалога
                users = []
                try:
                    # Получаем информацию о собеседнике
                    if peer_id > 0:
                        user_info = vk.users.get(user_ids=peer_id)[0]
                        users.append(f"{user_info['first_name']} {user_info['last_name']}")
                    users.append("ты")
                    users.append("я")
                except:
                    users = ["ты", "я", "он", "она", "оно"]
                
        except Exception as e:
            print(f"Ошибка получения участников: {e}")
            users = ["Анна", "Максим", "Дмитрий", "Екатерина", "Иван"]
        
        # Выбираем случайного пользователя
        selected = random.choice(users)
        
        if question:
            # Проверяем, нужно ли добавить "это"
            if question.lower().startswith(('это', 'этот', 'эта', 'этот', 'эти')):
                response = f"Что-то мне подсказывает, что {selected} {question}"
            else:
                response = f"Что-то мне подсказывает, что это {selected} {question}"
        else:
            response = f"Что-то мне подсказывает, что это {selected}"
        
        vk.messages.send(
            peer_id=peer_id,
            message=response,  # Убрано форматирование **
            random_id=0
        )
        
        return ""
        
    except Exception as e:
        print(f"Ошибка в .kto: {e}")
        return ""

def process_vos(clean_command, vk, message_id, peer_id, user_id):
    """Обрабатывает .vos <вопрос>"""
    
    try:
        # Удаляем сообщение команды
        try:
            vk.messages.delete(message_ids=message_id, delete_for_all=1)
        except:
            pass
        
        # Получаем вопрос
        question = clean_command[5:].strip()  # Убираем ".vos " или ".шар "
        
        # Ответы шара
        answers = [
            "Бесспорно",
            "Предрешено", 
            "Никаких сомнений",
            "Определённо да",
            "Можешь быть уверен в этом",
            "Мне кажется — да",
            "Вероятнее всего",
            "Хорошие перспективы",
            "Знаки говорят — да",
            "Да",
            "Пока не ясно, попробуй снова",
            "Спроси позже",
            "Лучше не рассказывать",
            "Сейчас нельзя предсказать",
            "Сконцентрируйся и спроси опять",
            "Даже не думай",
            "Мой ответ — нет",
            "По моим данным — нет",
            "Перспективы не очень хорошие",
            "Весьма сомнительно"
        ]
        
        # Случайный ответ
        answer = random.choice(answers)
        
        if question:
            response = f"🎱 {question}\n\nОтвет шара: {answer}"  # Убрано форматирование **
        else:
            response = f"🎱 Ответ шара: {answer}"  # Убрано форматирование **
        
        vk.messages.send(
            peer_id=peer_id,
            message=response,
            random_id=0
        )
        
        return ""
        
    except Exception as e:
        print(f"Ошибка в .vos: {e}")
        return ""