from pytz import timezone as tzone
from random import choice
from telegram import InputMediaPhoto
from time import sleep

from bot import LOGGER, PROG_UNFINISH, TIME_ZONE, PROG_FINISH, PROG_UNFINISH

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
        return 'File terlalu besar'


def progress_bar(percentage):
    if isinstance(percentage, str):
        return 'NaN'
    try:
        percentage = int(percentage)
    except:
        percentage = 0
    return ''.join(PROG_FINISH if i <= percentage // 10 else PROG_UNFINISH for i in range(1, 11))


def callender(dtime):
    dt_date = dtime.astimezone(tzone(TIME_ZONE)).strftime('%B %d, %Y')
    dt_time = dtime.astimezone(tzone(TIME_ZONE)).strftime('%H:%M:%S')
    return dt_date, dt_time


def sendMessage(text, bot, message, reply_markup=None):
    try:
        return bot.sendMessage(message.chat.id,
                               text=text,
                               parse_mode='HTML',
                               reply_to_message_id=message.message_id,
                               reply_markup=reply_markup,
                               disable_web_page_preview=True)
    except Exception as err:
        LOGGER.error(err)


def sendPhoto(caption, bot, message, photo, reply_markup=None):
    try:
        return bot.sendPhoto(chat_id=message.chat.id,
                             caption=caption,
                             photo=choice(photo),
                             reply_to_message_id=message.message_id,
                             parse_mode='HTML',
                             reply_markup=reply_markup)
    except Exception as err:
        LOGGER.error(err)


def editPhoto(caption, bot, message, photo, reply_markup=None):
    try:
        return bot.editMessageMedia(chat_id=message.chat.id,
                                    message_id=message.message_id,
                                    media=InputMediaPhoto(media=choice(photo),
                                                          caption=caption,
                                                          parse_mode='HTML'),
                                    reply_markup=reply_markup)
    except Exception as err:
        LOGGER.error(err)


def editMessage(text, bot, message):
    try:
        return bot.editMessageText(text=text,
                                   chat_id=message.chat.id,
                                   message_id=message.message_id,
                                   parse_mode='HTML')
    except Exception as err:
        LOGGER.error(err)


def deleteMessage(bot, message):
    try:
        return bot.deleteMessage(chat_id=message.chat.id, message_id=message.message_id)
    except Exception as err:
        LOGGER.error(err)
