from dotenv import load_dotenv
from faulthandler import enable as faulthandler_enable
from logging import getLogger, FileHandler, StreamHandler, INFO, basicConfig, error as log_error, info as log_info, warning as log_warning
from os import environ, path as ospath
from socket import setdefaulttimeout
from telegram.ext import Updater as tgUpdater
from time import time

if ospath.exists('log.txt'):
    with open('log.txt', 'r+') as f:
        f.truncate(0)

faulthandler_enable()

setdefaulttimeout(600)

basicConfig(format="%(asctime)s - [%(filename)s: %(lineno)d] - %(levelname)s - %(message)s",
            handlers=[FileHandler("log.txt"), StreamHandler()],
            level=INFO,)

LOGGER = getLogger(__name__)

load_dotenv("config.env", override=True)

botStartTime = time()

BOT_TOKEN = environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    LOGGER.info("BOT_TOKEN variable is missing! Exiting now")
    exit(1)
OWNER_ID = int(environ.get("OWNER_ID"))
if not OWNER_ID:
    LOGGER.info("OWNER_ID variable is missing! Exiting now")
    exit(1)
CHANNEL_ID = (environ.get("CHANNEL_ID", ""))
CHANNEL_ID = int(CHANNEL_ID) if CHANNEL_ID else None
SEND_LOG = environ.get("SEND_LOG", "false").lower() == "true"
HIDE_ID = environ.get("HIDE_ID", "False").lower() == "true"
PRIVATE_MODE = environ.get("PRIVATE_MODE", "True").lower() == "true"
TIME_ZONE = environ.get("TIME_ZONE", "Asia/Jakarta")
PICS_WARP = environ.get("PICS_WARP", "https://telegra.ph/file/f6d61498449f00b746aba.png https://telegra.ph/file/eeec153170e89e8aa42f9.png https://telegra.ph/file/56be1d4ed6abb49289bf9.png https://telegra.ph/file/0f34880fd920c914dad7d.png https://telegra.ph/file/417c202984dada6a2f2ad.png").split()
PICS_STATS = environ.get("PICS_STATS", "https://i.postimg.cc/gjRYbVzZ/warp.png").split()
COOLDOWN = int(environ.get("COOLDOWN", 20))
TASK_MAX = int(environ.get("TASK_MAX", 5))
PROG_FINISH = environ.get("PROG_FINISH", "⬢")
PROG_UNFINISH = environ.get("PROG_UNFINISH", "⬡")
START_CMD = environ.get("START_CMD", "start")
STATS_CMD = environ.get("STATS_CMD", "stats")
RESTART_CMD = environ.get("RESTART_CMD", "restart")
LOG_CMD = environ.get("LOG_CMD", "log")

updater = tgUpdater(token=BOT_TOKEN, request_kwargs={'read_timeout': 20, 'connect_timeout': 15})
bot = updater.bot
dispatcher = updater.dispatcher
job_queue = updater.job_queue
botname = bot.username
