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