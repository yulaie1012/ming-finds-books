# 用來初始化 LINE BOT

import os

from flask import Flask
from linebot import LineBotApi, WebhookHandler
import configparser
app = Flask(__name__)


config = configparser.ConfigParser()
config.read('config.ini')

line_bot_api = LineBotApi(os.environ['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['CHANNEL_SECRET'])

from app import routes, models_for_line