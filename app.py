import os
import time
import random
import pandas as pd
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup

app = Flask(__name__)
line_bot_api = LineBotApi(os.environ['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['CHANNEL_SECRET'])

@app.route("/", methods=['GET'])
def hello():
    return "Hello World!"

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OKK'

urltest = "https://libholding.ntut.edu.tw/webpacIndex.jsp"
driver = webdriver.Chrome("C:\\Users\mayda\Downloads\chromedriver") 
driver.get(urltest)

@handler.add(MessageEvent, message=TextMessage)
def NTNU_crawling(driver):
    ISBN = event.message.text
    element = driver.find_element_by_id('search_inputS')
    element.send_keys(ISBN)
    select = Select(driver.find_element_by_id('search_field'))
    select.select_by_value("STANDARDNO")
    search_gogogo = driver.find_element_by_xpath('/html/body/div[2]/table/tbody/tr/td[1]/div/div/div[1]/div/div[1]/div/form/table/tbody/tr[2]/td/input[3]').click()

    time.sleep(5)
    output = []
    table = driver.find_element_by_class_name('order')
    trlist = table.find_elements_by_tag_name('tr')
    for row in trlist:
        tdlist = row.find_elements_by_tag_name('td')
        for sth in tdlist:
            output = tdlist[2].text, tdlist[8].text
            break
    return(output)

def handle_message(event):
    line_bot_api.reply_message(event.reply_token,output)

if __name__ == 'main':
    app.run(debug=True)