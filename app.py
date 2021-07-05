# 載入需要的模組
from __future__ import unicode_literals
import os
import time
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.models import *
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

app = Flask(__name__)

# LINE 聊天機器人的基本資料
line_bot_api = LineBotApi('rtut2oGaCBibk5DTObwKuFgQgD8rC7JazGdF9f68BIP/2lXU+bBWjm3JgHQtvh0iHySthUi2We1XPVlGTMCh9s8Q1IZZL58osZBRvyHz8GXOnp4cd959MMyh/bXZkpaqdOepM0vcrSXXZvHSzcolLQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('5fecbae22c9e1492decda139bd70fd70')

# 接收 LINE 的資訊
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


# 回傳訊息
@handler.add(MessageEvent, message=TextMessage)
def NTNU_crawling(event):
    #----------------取得userid-----------------
    user_id = event.source.user_id
    if user_id == '':
        user_id = event.source.user_id
    #----------------爬蟲-----------------    
    ISBN = event.message.text
    urltest = "https://libholding.ntut.edu.tw/webpacIndex.jsp"
    driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver") 
    driver.get(urltest)
    element = driver.find_element_by_id('search_inputS')
    element.send_keys(ISBN)
    select = Select(driver.find_element_by_id('search_field'))
    select.select_by_value("STANDARDNO")
    search_gogogo = driver.find_element_by_xpath('/html/body/div[2]/table/tbody/tr/td[1]/div/div/div[1]/div/div[1]/div/form/table/tbody/tr[2]/td/input[3]').click()

    time.sleep(5)
    output = str()
    table = driver.find_element_by_class_name('order')
    trlist = table.find_elements_by_tag_name('tr')
    for row in trlist:
        tdlist = row.find_elements_by_tag_name('td')
        for sth in tdlist:
            output = tdlist[2].text +" "+ tdlist[8].text
            break
    
    if event.source.user_id != "Udeadbeefdeadbeefdeadbeefdeadbeef":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=output)
        )

if __name__ == "__main__":
    app.run(debug=True)