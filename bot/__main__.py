from datetime import datetime as dt
from os import path as ospath, remove as osremove, execl as osexecl
from psutil import disk_usage, cpu_percent, swap_memory, cpu_count, virtual_memory, net_io_counters, boot_time
from pytz import UTC
from subprocess import check_output, run as srun
from sys import executable
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from threading import Thread
from time import time, sleep

from bot import LOG_CMD, RESTART_CMD, bot, botStartTime, dispatcher, updater, LOGGER, OWNER_ID, PICS_WARP, COOLDOWN, HIDE_ID, CHANNEL_ID, \
                SEND_LOG, TASK_MAX, START_CMD, STATS_CMD, PICS_STATS, PROG_FINISH as F, PROG_UNFINISH as UF
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
    last_commit = check_output(["git log -1 --date=short --pretty=format:'%cd\n<b>├ Commit Change:</b> %cr'"],
                               shell=True).decode() if ospath.exists('.git') else 'No UPSTREAM_REPO'
    stats = f'<b>UPSTREAM AND BOT STATUS</b>\n'\
            f'<b>┌ Commit Date:</b> {last_commit}\n'\
            f'<b>├ Bot Uptime:</b> {get_readable_time(time() - botStartTime)}\n'\
            f'<b>└ OS Uptime:</b> {get_readable_time(time() - boot_time())}\n\n'\
            f'<b>SYSTEM STATUS</b>\n'\
            f'<b>┌ SWAP:</b> {get_readable_file_size(swap_memory().total)}\n'\
            f'<b>├ Total Cores:</b> {cpu_count(logical=True)}\n'\
            f'<b>├ Physical Cores:</b> {cpu_count(logical=False)}\n'\
            f'<b>├ Upload:</b> {get_readable_file_size(net_io_counters().bytes_sent)}\n'\
            f'<b>├ Download:</b> {get_readable_file_size(net_io_counters().bytes_recv)}\n'\
            f'<b>├ Disk Free:</b> {get_readable_file_size(disk_usage("/")[2])}\n'\
            f'<b>├ Disk Used:</b> {get_readable_file_size(disk_usage("/")[1])}\n'\
            f'<b>├ Disk Space:</b> {get_readable_file_size(disk_usage("/")[0])}\n'\
            f'<b>├ Memory Free:</b> {get_readable_file_size(virtual_memory().available)}\n'\
            f'<b>├ Memory Used:</b> {get_readable_file_size(virtual_memory().used)}\n'\
            f'<b>├ Memory Total:</b> {get_readable_file_size(virtual_memory().total)}\n'\
            f'<b>├ CPU:</b> {progress_bar(cpu_percent(interval=1))} {cpu_percent(interval=1)}%\n' \
            f'<b>├ RAM:</b> {progress_bar(virtual_memory().percent)} {virtual_memory().percent}%\n' \
            f'<b>├ DISK:</b> {progress_bar(disk_usage("/")[3])} {disk_usage("/")[3]}%\n' \
            f'<b>└ SWAP:</b> {progress_bar(swap_memory().percent)} {swap_memory().percent}%'
    sendPhoto(stats, context.bot, update.message, PICS_STATS)


def start(update, context):
    sendMessage("Hai, saya adalah <b>Warp+ Injector</b>. Kirim saja ID Warp mu kesini...", context.bot, update.message)


def restart(update, context):
    if update.message.from_user.id != OWNER_ID:
        return sendMessage("<b>Upss...</b> Mau ngapain?!", context.bot, update.message)
    restart_message = sendMessage("<i>Memulai ulang...</i>", context.bot, update.message)
    srun(["python3", "update.py"])
    with open(".restartmsg", "w") as f:
        f.truncate(0)
        f.write(f"{restart_message.chat.id}\n{restart_message.message_id}\n")
    osexecl(executable, executable, "-m", "bot")


def send_log(update, context):
    if update.message.from_user.id != OWNER_ID:
        return sendMessage("<b>Upss...</b> Mau ngapain?!", context.bot, update.message)
    update.message.reply_document(document=open("log.txt"))


def warp_handler(update, context):
    global data
    if data == TASK_MAX:
        return sendMessage("Cuma bisa jalanin satu tugas aja...", context.bot, update.message)
    msg = update.message.text
    if update.message.from_user.id != OWNER_ID:
        return sendMessage("<b>Upss...</b> Ini bot pribadi!", context.bot, update.message)
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
