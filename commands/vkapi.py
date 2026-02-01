import json

def process(clean_command, vk):
    """Обрабатывает команду .vkapi"""
    parts = clean_command[6:].strip().split(' ', 1)
    if len(parts) >= 1:
        method = parts[0]
        params = {}
        
        if len(parts) > 1:
            try:
                params = json.loads(parts[1])
            except:
                param_parts = parts[1].split('&')
                for param in param_parts:
                    if '=' in param:
                        key, value = param.split('=', 1)
                        params[key.strip()] = value.strip()
        
        try:
            result = vk._vk.method(method, params)
            result_message = f"✅ Команда выполнена успешно!\n\n📊 Результат:\n```json\n{json.dumps(result, indent=2, ensure_ascii=False)}\n```"
            return result_message
        except Exception as e:
            return f"❌ Ошибка выполнения команды VK API: {str(e)}"
    else:
        return "❌ Укажите метод VK API: .vkapi <метод> [параметры]\nПример: .vkapi users.get user_ids=1"