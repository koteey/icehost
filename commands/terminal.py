import subprocess

def process(clean_command):
    """Обрабатывает команду .terminal"""
    if len(clean_command) > 9:
        cmd = clean_command[9:].strip()
        return execute_terminal_command(cmd)
    else:
        return "❌ Укажите команду для выполнения: .terminal <команда>"

def execute_terminal_command(command):
    """Выполняет команду в терминале и возвращает результат"""
    try:
        # Выполняем команду без ограничений
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        
        output = ""
        if result.stdout:
            output += f"📤 STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"❌ STDERR:\n{result.stderr}\n"
        
        if output:
            # Обрезаем слишком длинный вывод
            if len(output) > 2000:
                output = output[:2000] + "\n... (вывод обрезан)"
            return f"💻 Команда: `{command}`\n\n{output}\n⏩ Код возврата: {result.returncode}"
        else:
            return f"💻 Команда: `{command}`\n\n✅ Выполнено успешно\n⏩ Код возврата: {result.returncode}"
            
    except subprocess.TimeoutExpired:
        return f"❌ Команда `{command}` превысила лимит времени (30 секунд)"
    except Exception as e:
        return f"❌ Ошибка выполнения команды: {str(e)}"