from .info import process as process_info
from .ping import process as process_ping
from .settings import process as process_settings
from .terminal import process as process_terminal
from .python import process as process_python
from .backupall import process as process_backupall
from .restoreall import process as process_restoreall
from .restart import process as process_restart
from .accountinfo import process as process_accountinfo
from .vkapi import process as process_vkapi
from .post import process as process_post
from .setname import process as process_setname
from .hotkey import process as process_hotkey
from .modules_cmd import process as process_modules_cmd
from .help import process_help_command as process_help
from .all_messages import process_all_messages, process_reply_messages, process_other_events
from .meme import process as process_meme
from .filter import process as process_filter
from .pitch import process_pitch, process_speed
from .random import (
    process_random, process_dice, process_coin, 
    process_chance, process_kto, process_vos
)
from .qr import process_qr, process_qrscan
from .davatar import process_davatar
from .ubac import process_ubac

# Медиа команды
from .copy import process as process_copy
from .spam import process as process_spam
from .negative import process as process_negative
from .demot import process as process_demot
from .text import process as process_text
from .setphoto import process as process_setphoto
from .dist import process as process_dist
from .boost import process as process_boost

def process_command(vk, peer_id, message_id, command, hotkeys, modules, settings, USER_ID):
    """Обрабатывает команды"""
    result_message = ""
    prefix = settings['prefix']
    
    if not command.startswith(prefix):
        return ""
    
    clean_command = command[len(prefix):]
    
    # Перехват команд модулями
    for module_name, module in modules.items():
        try:
            if hasattr(module, 'on_command_intercept'):
                intercept_result = module.on_command_intercept(
                    command=clean_command,
                    vk=vk,
                    peer_id=peer_id,
                    message_id=message_id,
                    user_id=USER_ID,
                    settings=settings
                )
                if intercept_result is not None:
                    return intercept_result
        except:
            pass
    
    command_name = clean_command.split()[0] if ' ' in clean_command else clean_command
    
    # Основные команды
    if command_name == 'info':
        result_message = process_info(vk, settings, USER_ID)
    
    elif command_name == 'ping':
        result_message = process_ping(vk, settings)
    
    elif command_name == 'settings':
        result_message = process_settings(clean_command, settings, hotkeys, vk, message_id, peer_id)
    
    elif command_name == 'terminal':
        result_message = process_terminal(clean_command)
    
    elif command_name == 'python':
        result_message = process_python(clean_command)
    
    elif command_name == 'backupall':
        result_message = process_backupall(vk, settings, USER_ID)
    
    elif command_name == 'restoreall':
        result_message = process_restoreall(vk, message_id, peer_id, USER_ID)
    
    elif command_name == 'restart':
        result_message = process_restart(vk, peer_id, message_id)
    
    elif command_name == 'accountinfo':
        result_message = process_accountinfo(vk, USER_ID)
    
    elif command_name == 'vkapi':
        result_message = process_vkapi(clean_command, vk)
    
    elif command_name == 'post':
        result_message = process_post(clean_command, vk, message_id, peer_id, USER_ID)
    
    elif command_name == 'setname':
        result_message = process_setname(clean_command, vk)
    
    elif command_name in ['hotkey', 'hotlist', 'delhotkey']:
        result_message = process_hotkey(clean_command, hotkeys, settings)
    
    elif command_name in ['modules', 'dm', 'delm']:
        result_message = process_modules_cmd(clean_command, vk, message_id, peer_id, modules)
    
    # Медиа команды
    elif command_name == 'copy':
        process_copy(clean_command, vk, message_id, peer_id, USER_ID)
        return ""
    
    elif command_name == 'spam':
        process_spam(clean_command, vk, peer_id, USER_ID)
        return ""
    
    elif command_name in ['negative', 'n']:
        process_negative(clean_command, vk, message_id, peer_id, USER_ID)
        return ""
    
    elif command_name == 'demot':
        process_demot(clean_command, vk, message_id, peer_id, USER_ID)
        return ""
    
    elif command_name == 'text':
        process_text(clean_command, vk, message_id, peer_id, USER_ID)
        return ""
    
    elif command_name == 'setphoto':
        process_setphoto(clean_command, vk, message_id, peer_id, USER_ID)
        return ""
    
    elif command_name in ['dist', 'd']:
        process_dist(clean_command, vk, message_id, peer_id, USER_ID)
        return ""
    
    elif command_name in ['boost', 'bu']:
        process_boost(clean_command, vk, message_id, peer_id, USER_ID)
        return ""

    elif command_name in ['meme', 'мем']:
        process_meme(clean_command, vk, message_id, peer_id, USER_ID)
        return ""

    elif command_name == 'filter':
        process_filter(clean_command, vk, message_id, peer_id, USER_ID)
        return ""

    elif command_name == 'pitch':
        process_pitch(clean_command, vk, message_id, peer_id, USER_ID)
        return ""

    elif command_name == 'speed':
        process_speed(clean_command, vk, message_id, peer_id, USER_ID)
        return ""

    elif command_name == 'random':
        process_random(clean_command, vk, message_id, peer_id, USER_ID)
        return ""

    elif command_name == 'dice':
        process_dice(clean_command, vk, message_id, peer_id, USER_ID)
        return ""

    elif command_name == 'coin':
        process_coin(clean_command, vk, message_id, peer_id, USER_ID)
        return ""

    elif command_name == 'chance':
        process_chance(clean_command, vk, message_id, peer_id, USER_ID)
        return ""

    elif command_name in ['kto', 'кто']:
        process_kto(clean_command, vk, message_id, peer_id, USER_ID)
        return ""

    elif command_name in ['vos', 'вос', 'шар']:
        process_vos(clean_command, vk, message_id, peer_id, USER_ID)
        return ""






    elif command_name == 'qr':
        process_qr(clean_command, vk, message_id, peer_id, USER_ID)
        return ""

    elif command_name == 'qrscan':
        process_qrscan(clean_command, vk, message_id, peer_id, USER_ID)
        return ""

    elif command_name == 'davatar':
        process_davatar(clean_command, vk, message_id, peer_id, USER_ID)
        return ""

    elif command_name == 'ubac':
        process_ubac(clean_command, vk, message_id, peer_id, USER_ID)
        return ""
    # Команды помощи (все 4 варианта)
    elif command_name in ['help', '911', '112', 'sos']:
        result_message = process_help(command, prefix)
    
    else:
        # Проверяем модули
        for module_name, module in modules.items():
            try:
                if settings and '_utils' not in settings:
                    from lib.system_utils import get_module_utils
                    settings['_utils'] = get_module_utils()
                
                module_result = module.process_command(clean_command, vk, peer_id, USER_ID, settings)
                if module_result:
                    result_message = module_result
                    break
            except TypeError:
                try:
                    module_result = module.process_command(clean_command, vk, peer_id, USER_ID)
                    if module_result:
                        result_message = module_result
                        break
                except:
                    pass
            except:
                pass
    
    # Если команда не обработана
    if not result_message and clean_command:
        result_message = f"""❌ Неизвестная команда: `{command}`

💡 Используйте `{prefix}help` для просмотра всех команд"""
    
    return result_message