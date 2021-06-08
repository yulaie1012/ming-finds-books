# 用來初始化 LINE BOT

import os
from flask import Flask
from linebot import LineBotApi, WebhookHandler
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")

from selenium import webdriver # 先下載 webdriver
chrome_options = webdriver.ChromeOptions()
driver = webdriver.Chrome(executable_path=os.environ.get("C:\\Users\mayda\Downloads\chromedriver"), chrome_options=chrome_options)


app = Flask(__name__)

line_bot_api = LineBotApi(os.environ['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['CHANNEL_SECRET'])

from app import routes, models_for_line