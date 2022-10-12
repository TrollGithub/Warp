import datetime
import json
import random
import string
import urllib.request

from datetime import datetime as dt
from pytz import UTC
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from time import time, sleep

from bot import warp_data, COOLDOWN, LOGGER, HIDE_ID, CHANNEL_ID, PROG_FINISH, PROG_UNFINISH, SEND_LOG, PICS_WARP, TIME_ZONE_TITLE
from bot.helpers.utils import callender, editPhoto, get_readable_time, get_readable_file_size


LOGGER.info("WARP+ Cloudflare")

def genString(stringLength):
    try:
        letters = string.ascii_letters + string.digits
        return ''.join(random.choice(letters) for i in range(stringLength))
    except Exception as error:
        LOGGER.error(error)

def digitString(stringLength):
    try:
        digit = string.digits
        return ''.join((random.choice(digit) for i in range(stringLength)))
    except Exception as error:
        LOGGER.error(error)

url = f'https://api.cloudflareclient.com/v0a{digitString(3)}/reg'

def run(warp_id):
    try:
        install_id = genString(22)
        body = {"key": "{}=".format(genString(43)),
                "install_id": install_id,
                "fcm_token": "{}:APA91b{}".format(install_id, genString(134)),
                "referrer": warp_id,
                "warp_enabled": False,
                "tos": datetime.datetime.now().isoformat()[:-3] + "+02:00",
                "type": "Android",
                        "locale": "es_ES"}
        data = json.dumps(body).encode('utf8')
        headers = {'Content-Type': 'application/json; charset=UTF-8',
                   'Host': 'api.cloudflareclient.com',
                   'Connection': 'Keep-Alive',
                   'Accept-Encoding': 'gzip',
                   'User-Agent': 'okhttp/3.12.1'}
        req = urllib.request.Request(url, data, headers)
        response = urllib.request.urlopen(req)
        status_code = response.getcode()
        return status_code
    except Exception as error:
        LOGGER.error(f"Error: {error}")

def warp_run(bot, user_id, warp_id, wrap_msg):
    g = 0
    b = 0
    bw = 0
    start_time = time()
    button = [[InlineKeyboardButton(text="Stop", callback_data=user_id)]]
    while True:
        warp_dict = warp_data.get(user_id, False)
        date_add, time_added = callender(dt.now(tz=UTC))
        msg_log = f"<b>├ Received:</b> {get_readable_file_size(bw)}\n"
        msg_log += f"<b>├ Success:</b> {g}\n"
        msg_log += f"<b>├ Failed:</b> {b}\n"
        msg_log += f"<b>├ Total:</b> {g + b}\n"
        msg_log += f"<b>├ Elapsed:</b> {get_readable_time(time() - start_time)}\n"
        msg_log += f"<b>├ Time:</b> {time_added} ({TIME_ZONE_TITLE})\n"
        msg_log += f"<b>└ Add:</b> {date_add}"
        f = PROG_FINISH
        uf = PROG_UNFINISH
        prgss_bar = [f*2 + uf*8, f*4 + uf*6, f*6 + uf*4, f*8 + uf*2, f*10]
        prgss_prcn = ["20%", "40%", "60%", "80%", "100%"]
        for i in range(len(prgss_bar)):
            caption = "<b>WARP+ INJECTOR</b>\n"
            if not HIDE_ID:
                caption += f"<code>{warp_id}</code>\n"
            caption += f"<b>┌ </b>{prgss_bar[i % len(prgss_bar)]}\n"
            caption += f"<b>├ Progress:</b> {prgss_prcn[i % len(prgss_bar)]}\n"
            caption += msg_log
            if not warp_dict.get('run_warp'):
                break
            else:
                editPhoto(caption, bot, wrap_msg, PICS_WARP, InlineKeyboardMarkup(button))
                sleep(3)
        result = run(warp_id)
        if result == 200:
            g += 1
            bw += 1 * 1024**3
            if SEND_LOG:
                bot.send_message(CHANNEL_ID, text=msg_log, parse_mode='HTML')
            for i in range(COOLDOWN, -1, -5):
                caption = "<b>WARP+ INJECTOR</b>\n"
                if not HIDE_ID:
                    caption += f"<code>{warp_id}</code>\n"
                caption += f"<b>┌ Cooldown:</b> {i} detik...\n"
                caption += f"<b>├ Progress:</b> 0%\n"
                caption += msg_log
                if not warp_dict.get('run_warp'):
                    break
                else:
                    editPhoto(caption, bot, wrap_msg, PICS_WARP, InlineKeyboardMarkup(button))
                    sleep(5)
        else:
            b += 1
            LOGGER.info(f"Total: {g} Good {b} Bad")
            for i in range(COOLDOWN, -1, -5):
                caption = "<b>WARP+ INJECTOR</b>\n"
                if not HIDE_ID:
                    caption += f"<code>{warp_id}</code>\n"
                caption += f"<b>┌ Cooldown:</b> {i} detik...\n"
                caption += f"<b>├ Progress:</b> 0%\n"
                caption += msg_log
                if not warp_dict.get('run_warp'):
                    break
                else:
                    editPhoto(caption, bot, wrap_msg, PICS_WARP, InlineKeyboardMarkup(button))
                    sleep(5)
        if not warp_dict.get('run_warp'):
            LOGGER.info(f"Task stopped!: {warp_id}")
            caption = "<b>TASK STOPPED!</b>\n"
            if not HIDE_ID:
                caption += f"<code>{warp_id}</code>\n"
            caption += f"<b>┌ Received: </b>{get_readable_file_size(bw)}\n"
            caption += f"<b>├ Task Success: </b>{g}\n"
            caption += f"<b>├ Task Failed: </b>{b}\n"
            caption += f"<b>├ Task Total: </b>{g + b}\n"
            caption += f"<b>└ Elapsed: </b>{get_readable_time(time() - start_time)}"
            editPhoto(caption, bot, wrap_msg, PICS_WARP)
            break