import io
import contextlib

def process(clean_command):
    """Обрабатывает команду .python"""
    if len(clean_command) > 7:
        code = clean_command[7:].strip()
        # Декодируем HTML-сущности
        code = code.replace('&quot;', '"').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        return execute_python_code(code)
    else:
        return "❌ Укажите код Python: .python <код>"

def execute_python_code(code):
    """Выполняет код Python и возвращает результат"""
    try:
        # Создаем контекст для перехвата вывода
        output = io.StringIO()
        
        with contextlib.redirect_stdout(output):
            with contextlib.redirect_stderr(output):
                try:
                    # Выполняем код с полным доступом
                    exec(code)
                    
                    # Если код выглядит как выражение, пытаемся его вычислить
                    if any(indicator in code for indicator in ['+', '-', '*', '/', '=', '==', '!=', '>', '<']):
                        try:
                            eval_result = eval(code)
                            if eval_result is not None and str(eval_result) not in output.getvalue():
                                print(f"📦 Результат: {eval_result}")
                        except:
                            pass  # Игнорируем ошибки eval, если exec уже сработал
                            
                except Exception as e:
                    print(f"❌ Ошибка выполнения: {type(e).__name__}: {e}")
        
        result_output = output.getvalue()
        
        if result_output:
            # Обрезаем слишком длинный вывод
            if len(result_output) > 2000:
                result_output = result_output[:2000] + "\n... (вывод обрезан)"
            return f"🐍 Код:\n```python\n{code}\n```\n\n📤 Вывод:\n{result_output}"
        else:
            return f"🐍 Код:\n```python\n{code}\n```\n\n✅ Выполнено без вывода"
            
    except Exception as e:
        return f"❌ Ошибка выполнения Python кода: {str(e)}"