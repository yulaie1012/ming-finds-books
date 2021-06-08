# 用來初始化 LINE BOT

import os

from flask import Flask
from linebot import LineBotApi, WebhookHandler
import configparser
from selenium import webdriver # 先下載 webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['CHANNEL_SECRET'])

from app import routes, models_for_line