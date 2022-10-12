from os import path as ospath, remove as osremove, execl as osexecl
from platform import system, architecture, release
from psutil import disk_usage, cpu_percent, swap_memory, cpu_count, virtual_memory, net_io_counters, boot_time
from subprocess import check_output, run as srun
from sys import executable
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from threading import Thread
from time import time, sleep

from bot import bot, botStartTime, dispatcher, updater, warp_data, LOG_CMD, RESTART_CMD, LOGGER, OWNER_ID, PICS_WARP, COOLDOWN, \
                TASK_MAX, START_CMD, STATS_CMD, PICS_STATS, PRIVATE_MODE
from bot.helpers.utils import sendMessage, deleteMessage, sendPhoto, get_readable_time, \
                              get_readable_file_size, progress_bar, update_warp_data
from bot.helpers.warp_plus import warp_run


task_run = 0


def start(update, context):
    sendMessage("This is <b>Warp+ Injector</b>. Just send your id here...", context.bot, update.message)

def stats(update, context):
    if PRIVATE_MODE:
        return sendMessage("<b>Upss...</b> private mode active! Contact the owner to make it public access!", context.bot, update.message)
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

def send_log(update, context):
    if update.message.from_user.id != OWNER_ID:
        return sendMessage("<b>Upss...</b> You can't do this, owner only!", context.bot, update.message)
    update.message.reply_document(document=open("log.txt"))

def restart(update, context):
    if update.message.from_user.id != OWNER_ID:
        return sendMessage("<b>Upss...</b> You can't do this, owner only!", context.bot, update.message)
    restart_message = sendMessage("<i>Resatarting...</i>", context.bot, update.message)
    srun(["python3", "update.py"])
    with open(".restartmsg", "w") as f:
        f.truncate(0)
        f.write(f"{restart_message.chat.id}\n{restart_message.message_id}\n")
    osexecl(executable, executable, "-m", "bot")

def warp_handler(update, context):
    global task_run
    if PRIVATE_MODE:
        return sendMessage("<b>Upss...</b> private mode active! Contact the owner to make it public access!", context.bot, update.message)
    msg = update.message.text
    user_id = update.message.from_user.id
    warp_dict = warp_data.get(user_id, False)
    if warp_dict and warp_dict.get("run_warp"):
            return sendMessage(f"Ups, you can only add 1 task!", context.bot, update.message)
    if TASK_MAX != -1:
        if task_run == TASK_MAX:
            return sendMessage(f"Ups, bot task limit is {TASK_MAX}!", context.bot, update.message)
    if len(msg) != 36:
        return
    if "-" not in msg:
        return sendMessage("Invalid ID!", context.bot, update.message)
    wrap_msg = sendMessage("<i>Cheching your ID, please wait...</i>", context.bot, update.message)
    LOGGER.info(f"Found Warp ID: {msg}")
    sleep(3)
    deleteMessage(bot, wrap_msg)
    uname = f"<a href='https://t.me/{user_id}'>{update.message.from_user.first_name}</a>"
    caption = f"{uname}... This ID will proccess to added 1GB warp+ quota every {COOLDOWN} seconds...\n<code>{msg}</code>"
    wrap_msg = sendPhoto(caption, context.bot, update.message, PICS_WARP)
    update_warp_data(user_id, 'run_warp', True)
    sleep(5)
    Thread(target=warp_run, args=(context.bot, user_id, msg, wrap_msg)).start()
    task_run += 1

def stop_query(update, context):
    query = update.callback_query
    user_id = query.message.reply_to_message.from_user.id
    if user_id != int(query.data) or user_id != OWNER_ID: # Future for group support
        return query.answer(text="Not Your Task!", show_alert=True)
    else:
        query.answer(text="Your Task Has Been Cancelled!", show_alert=True)
        update_warp_data(user_id, 'run_warp', False)

def main():
    if ospath.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
        msg = 'Restart Successfully!'
    else:
        msg = '⚡️ Bot Ready...'
    if 'Restart Successfully!' in msg:
        bot.editMessageText(text=msg, chat_id=chat_id, message_id=msg_id)
        osremove(".restartmsg")
    else:
        bot.sendMessage(OWNER_ID, msg, parse_mode='HTML')
    dispatcher.add_handler(CommandHandler(START_CMD, start))
    dispatcher.add_handler(CommandHandler(STATS_CMD, stats))
    dispatcher.add_handler(CommandHandler(RESTART_CMD, restart))
    dispatcher.add_handler(CommandHandler(LOG_CMD, send_log))
    dispatcher.add_handler(CallbackQueryHandler(stop_query, run_async=True))
    dispatcher.add_handler(MessageHandler(Filters.text, warp_handler))
    updater.start_polling(drop_pending_updates=True)
    LOGGER.info("Bot Started!")

main()
