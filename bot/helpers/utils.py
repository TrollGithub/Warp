from random import choice
from telegram import InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup

from bot import warp_data, LOGGER, PROG_UNFINISH, PROG_FINISH, PROG_UNFINISH, OWNER_ID


SIZE_UNITS = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']

def get_readable_time(seconds: int) -> str:
    result = ''
    (days, remainder) = divmod(seconds, 86400)
    days = int(days)
    if days != 0:
        result += f'{days}d '
    (hours, remainder) = divmod(remainder, 3600)
    hours = int(hours)
    if hours != 0:
        result += f'{hours}h '
    (minutes, seconds) = divmod(remainder, 60)
    minutes = int(minutes)
    if minutes != 0:
        result += f'{minutes}m '
    seconds = int(seconds)
    result += f'{seconds}s'
    return result

def update_warp_data(id_: int, key, value):
    if id_ in warp_data:
        warp_data[id_][key] = value
    else:
        warp_data[id_] = {key: value}

def get_readable_file_size(size_in_bytes) -> str:
    if size_in_bytes is None:
        return '0B'
    index = 0
    while size_in_bytes >= 1024:
        size_in_bytes /= 1024
        index += 1
    try:
        return f'{round(size_in_bytes, 2)}{SIZE_UNITS[index]}'
    except IndexError:
        return 'File to big.'

def progress_bar(percentage):
    if isinstance(percentage, str):
        return 'NaN'
    try:
        percentage = int(percentage)
    except:
        percentage = 0
    return ''.join(PROG_FINISH if i <= percentage // 10 else PROG_UNFINISH for i in range(1, 11))

def get_button(text, key, user_id=None):
    return InlineKeyboardMarkup([[InlineKeyboardButton(text=text, callback_data=f"{user_id if user_id else OWNER_ID} {key}")]])

def get_data():
    with open(".mode.txt", "r") as file:
        file = file.read()
        update_warp_data(OWNER_ID, "private_mode", True if file == "True" else False)
    return warp_data.get(OWNER_ID, False)

def sendMessage(text, bot, message, reply_markup=None):
    try:
        return bot.sendMessage(message.chat.id, text=text,
                               reply_to_message_id=message.message_id,
                               reply_markup=reply_markup)
    except Exception as err:
        LOGGER.error(err)
        return

def sendPhoto(caption, bot, message, photo, reply_markup=None):
    try:
        return bot.sendPhoto(chat_id=message.chat.id,
                             caption=caption, photo=choice(photo),
                             reply_to_message_id=message.message_id,
                             reply_markup=reply_markup)
    except Exception as err:
        LOGGER.error(err)
        return

def editPhoto(caption, bot, message, photo, reply_markup=None):
    try:
        bot.editMessageMedia(chat_id=message.chat.id,
                             message_id=message.message_id,
                             media=InputMediaPhoto(media=choice(photo), caption=caption),
                             reply_markup=reply_markup)
    except Exception as err:
        LOGGER.error(err)
        return str(err)

def deleteMessage(bot, message):
    try:
        bot.deleteMessage(chat_id=message.chat.id, message_id=message.message_id)
    except Exception as err:
        LOGGER.error(err)
