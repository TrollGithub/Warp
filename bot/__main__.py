from datetime import datetime as dt
from os import path as ospath, remove as osremove, execl as osexecl
from platform import system, architecture, release
from psutil import disk_usage, cpu_percent, swap_memory, cpu_count, virtual_memory, net_io_counters, boot_time
from pytz import UTC
from subprocess import check_output, run as srun
from sys import executable
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from threading import Thread
from time import time, sleep

from bot import LOG_CMD, RESTART_CMD, bot, botStartTime, dispatcher, updater, LOGGER, OWNER_ID, PICS_WARP, COOLDOWN, HIDE_ID, CHANNEL_ID, \
                SEND_LOG, TASK_MAX, START_CMD, STATS_CMD, PICS_STATS, PROG_FINISH as F, PROG_UNFINISH as UF, PRIVATE_MODE
from bot.helpers.utils import callender, editPhoto, sendMessage, deleteMessage, sendPhoto, get_readable_time, \
                              get_readable_file_size, progress_bar
from bot.helpers.warp_plus import run

stop_tred = False
task_ids = []
data = 0


def warp_run(bot, warp_id, wrap_msg):
    g = 0
    b = 0
    bw = 0
    start_time = time()
    ids = f"{str(wrap_msg.chat.id)[:4]}{wrap_msg.message_id}"
    button = [[InlineKeyboardButton(text="Stop", callback_data=f"warp {ids}")]]
    while True:
        global stop_tred
        date_add, time_added = callender(dt.now(tz=UTC))
        msg_log = f"<b>├ Diterima:</b> {get_readable_file_size(bw)}\n"
        msg_log += f"<b>├ Sukses:</b> {g}\n"
        msg_log += f"<b>├ Gagal:</b> {b}\n"
        msg_log += f"<b>├ Total:</b> {g + b}\n"
        msg_log += f"<b>├ Berlalu:</b> {get_readable_time(time() - start_time)}\n"
        msg_log += f"<b>├ Jam:</b> {time_added} W.I.B\n"
        msg_log += f"<b>└ Tanggal:</b> {date_add}"
        prgss_bar = [F*2 + UF*8, F*4 + UF*6, F*6 + UF*4, F*8 + UF*2, F*10]
        prgss_prcn = ["20%", "40%", "60%", "80%", "100%"]
        for i in range(len(prgss_bar)):
            caption = "<b>WARP+ INJECTOR</b>\n"
            if not HIDE_ID:
                caption += f"<code>{warp_id}</code>\n"
            caption += f"<b>┌ </b>{prgss_bar[i % len(prgss_bar)]}\n"
            caption += f"<b>├ Progress:</b> {prgss_prcn[i % len(prgss_bar)]}\n"
            caption += msg_log
            if stop_tred and ids in task_ids:
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
                caption += f"<b>┌ Waktu Tunggu:</b> {i} detik...\n"
                caption += f"<b>├ Progress:</b> 0%\n"
                caption += msg_log
                if stop_tred and ids in task_ids:
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
                caption += f"<b>┌ Waktu Tunggu:</b> {i} detik...\n"
                caption += f"<b>├ Progress:</b> 0%\n"
                caption += msg_log
                if stop_tred and ids in task_ids:
                    break
                else:
                    editPhoto(caption, bot, wrap_msg, PICS_WARP, InlineKeyboardMarkup(button))
                    sleep(5)
        if stop_tred and ids in task_ids:
            LOGGER.info(f"Tugas dihentikan: {warp_id}")
            caption = "<b>TUGAS DIHENTIKAN</b>\n"
            if not HIDE_ID:
                caption += f"<code>{warp_id}</code>\n"
            caption += f"<b>┌ BW diterima: </b>{get_readable_file_size(bw)}\n"
            caption += f"<b>├ Tugas Suskes: </b>{g}\n"
            caption += f"<b>├ Tugas gagal: </b>{b}\n"
            caption += f"<b>├ Tugas Tugas: </b>{g + b}\n"
            caption += f"<b>└ Waktu berlalu: </b>{get_readable_time(time() - start_time)}"
            editPhoto(caption, bot, wrap_msg, PICS_WARP)
            task_ids.remove(ids)
            break


def stats(update, context):
    if PRIVATE_MODE:
        return sendMessage("<b>Upss...</b> mode privat aktif! Silahkan minta pemilik untuk akses publik", context.bot, update.message)
    last_commit = check_output(["git log -1 --date=short --pretty=format:'%cd\n<b>├ Commit Change:</b> %cr'"],
                               shell=True).decode() if ospath.exists('.git') else 'No UPSTREAM_REPO'
    stats = f'''
<b>UPSTREAM AND BOT STATUS</b>
<b>┌ Commit Date:</b> {last_commit}
<b>├ Bot Uptime:</b> {get_readable_time(time() - botStartTime)}
<b>└ OS Uptime:</b> {get_readable_time(time() - boot_time())}\n
<b>SYSTEM STATUS</b>
<b>┌ SWAP:</b> {get_readable_file_size(swap_memory().total)}
<b>├ Total Cores:</b> {cpu_count(logical=True)}
<b>├ Physical Cores:</b> {cpu_count(logical=False)}
<b>├ Upload:</b> {get_readable_file_size(net_io_counters().bytes_sent)}
<b>├ Download:</b> {get_readable_file_size(net_io_counters().bytes_recv)}
<b>├ Disk Free:</b> {get_readable_file_size(disk_usage("/")[2])}
<b>├ Disk Used:</b> {get_readable_file_size(disk_usage("/")[1])}
<b>├ Disk Space:</b> {get_readable_file_size(disk_usage("/")[0])}
<b>├ Memory Free:</b> {get_readable_file_size(virtual_memory().available)}
<b>├ Memory Used:</b> {get_readable_file_size(virtual_memory().used)}
<b>├ Memory Total:</b> {get_readable_file_size(virtual_memory().total)}
<b>├ CPU:</b> {progress_bar(cpu_percent(interval=1))} {cpu_percent(interval=1)}%
<b>├ RAM:</b> {progress_bar(virtual_memory().percent)} {virtual_memory().percent}%
<b>├ DISK:</b> {progress_bar(disk_usage("/")[3])} {disk_usage("/")[3]}%
<b>├ SWAP:</b> {progress_bar(swap_memory().percent)} {swap_memory().percent}%
<b>└ OS:</b> {system()}, {architecture()[0]}, {release()}
'''
    sendPhoto(stats, context.bot, update.message, PICS_STATS)


def start(update, context):
    sendMessage("Hai, saya adalah <b>Warp+ Injector</b>. Kirim saja ID Warp mu kesini...", context.bot, update.message)


def restart(update, context):
    if update.message.from_user.id != OWNER_ID:
        return sendMessage("<b>Upss...</b> Mau ngapain?! Khusus pemilik", context.bot, update.message)
    restart_message = sendMessage("<i>Memulai ulang...</i>", context.bot, update.message)
    srun(["python3", "update.py"])
    with open(".restartmsg", "w") as f:
        f.truncate(0)
        f.write(f"{restart_message.chat.id}\n{restart_message.message_id}\n")
    osexecl(executable, executable, "-m", "bot")


def send_log(update, context):
    if update.message.from_user.id != OWNER_ID:
        return sendMessage("<b>Upss...</b> Mau ngapain?! Khusus pemilik", context.bot, update.message)
    update.message.reply_document(document=open("log.txt"))


def warp_handler(update, context):
    global data
    if PRIVATE_MODE:
        return sendMessage("<b>Upss...</b> mode privat aktif! Solahkan minta pemilik untuk akses publik", context.bot, update.message)
    if data == TASK_MAX:
        return sendMessage(f"Cuma bisa jalanin {TASK_MAX} tugas aja...", context.bot, update.message)
    msg = update.message.text
    uname = f"<a href='https://t.me/{update.message.from_user.id}'>{update.message.from_user.first_name}</a>"
    if len(msg) != 36:
        return
    if "-" not in msg:
        return sendMessage("Kirim ID yang bener!", context.bot, update.message)
    data += 1
    wrap_msg = sendMessage("<i>Mengecek ID...</i>", context.bot, update.message)
    LOGGER.info(f"Menemukan Warp ID: {msg}")
    sleep(3)
    deleteMessage(bot, wrap_msg)
    caption = f"<code>{msg}</code>\n<b>{uname}...</b> ID berikut akan segera di proses untuk ditambahkan BW 1GB / {COOLDOWN} detik..."
    wrap_msg = sendPhoto(caption, context.bot, update.message, PICS_WARP)
    sleep(5)
    Thread(target=warp_run, args=(context.bot, msg, wrap_msg)).start()


def stop_query(update, context):
    global stop_tred
    query = update.callback_query
    query.answer()
    data = query.data.split()
    id = f"{str(query.message.chat.id)[:4]}{query.message.message_id}"
    if int(data[1]) == int(id):
        task_ids.append(data[1])
        stop_tred = True


def main():
    if ospath.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
        msg = 'Mulai ulang berhasil!'
    else:
        msg = '⚡️ Bot siap...!'
    if 'Mulai ulang berhasil!' in msg:
        bot.editMessageText(text=msg, chat_id=chat_id, message_id=msg_id)
        osremove(".restartmsg")
    else:
        bot.sendMessage(OWNER_ID, msg, parse_mode='HTML')
    dispatcher.add_handler(CommandHandler(START_CMD, start))
    dispatcher.add_handler(CommandHandler(STATS_CMD, stats))
    dispatcher.add_handler(CommandHandler(RESTART_CMD, restart))
    dispatcher.add_handler(CommandHandler(LOG_CMD, send_log))
    dispatcher.add_handler(CallbackQueryHandler(stop_query, pattern="warp", run_async=True))
    dispatcher.add_handler(MessageHandler(Filters.text, warp_handler))
    updater.start_polling(drop_pending_updates=True)
    LOGGER.info("Bot Started!")


main()
