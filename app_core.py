from __future__ import unicode_literals
import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from app import handler, line_bot_api

chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
from selenium import webdriver # 先下載 webdriver
chrome_options = webdriver.ChromeOptions()
driver = webdriver.Chrome(executable_path=os.environ.get("C:\\Users\mayda\Downloads\chromedriver"), chrome_options=chrome_options)


from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time

# 利用 handler 處理 LINE 觸發事件
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# LINE 聊天機器人的基本資料
line_bot_api = LineBotApi(os.environ['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['CHANNEL_SECRET'])

from app import app

if __name__ == "__main__":
    app.run()