# 載入需要的模組
from __future__ import unicode_literals
import os
import time
import json
import math
import flex_template
from flask import Flask, request, abort
#---------------------------------------
from linebot import LineBotApi, WebhookHandler, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.models import *
#---------------------------------------
from selenium import webdriver
from selenium.webdriver.chrome.options import Options  # 設定 driver 的行為
from selenium.webdriver.support.ui import Select  # 選擇＂下拉式選單＂
from selenium.webdriver.common.keys import Keys  # 鍵盤操作
from selenium.common.exceptions import NoSuchElementException, TimeoutException  # 載入常見錯誤
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities  # 更改載入策略
from selenium.webdriver.support.ui import WebDriverWait  # 等待機制
from selenium.webdriver.support import expected_conditions as EC  # 預期事件
from selenium.webdriver.common.by import By  # 找尋元素的方法
#---------------------------------------
from google.oauth2 import service_account
from google.oauth2.service_account import Credentials
import gspread
import gspread_dataframe as gd
#---------------------------------------
import import_ipynb
import toread
import INSTs
from toread import toread, toread_crawlers, NTC, HWU, NDHU
from INSTs import organize_columns, wait_for_element_present, wait_for_url_changed, accurately_find_table_and_read_it, \
    search_ISBN, click_more_btn, TPML, webpac_jsp_crawler, FGU, select_ISBN_strategy, NTOU, \
    easy_crawler, NYCU, NTNU, NTUST, PCCU, FJU, SINICA, webpac_pro_crawler, webpac_ajax_page_crawler, NTPC, KLCCAB, \
    基隆市公共圖書館, webpac_gov_crawler, ILCCB, wait_for_element_clickable, NIU, 國家圖書館, NCL, CYCU, \
    primo_crawler, NTU, NCCU, primo_greendot_crawler, CGU, primo_greendot_finding, primo_finding, CYUT, \
    FCU, NSYSU, NKNU, WZU, Tajen, NCU, CUST, CNU, NTUA, UTaipei, NTUT, TMU, NTUB, Miaoli, JUST, CLUT, VNU, UCH, \
    MUST, YDU, CUTE, MMC, ITRI, NTCU, NTUS, THU, PU, OCU, NCUE, YLCCB, TYPL, KSML, PTPL

scope = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_service_account_file("C:\\Users\mayda\Downloads\\books-319701-17701ae5510b.json", scopes=scope)
gs = gspread.authorize(creds)
sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
worksheet = sheet.get_worksheet(0)


#----------------用來做縣市對應region字典-----------------
north = ["台北市","新北市","基隆市","桃園市","苗栗縣","新竹縣","新竹市","臺北市", "連江縣"]
center = ["台中市","彰化縣","南投縣","雲林縣","臺中市", "金門縣"]
south = ["嘉義市","台南市","高雄市","屏東縣","臺南市", "澎湖縣"]
east = ["宜蘭縣","花蓮縣","台東縣","臺東縣"]
n_dict = dict.fromkeys(north, ("北","north"))
c_dict = dict.fromkeys(center, ("中","center"))
s_dict = dict.fromkeys(south, ("南","south"))
e_dict = dict.fromkeys(east, ("東","east"))

app = Flask(__name__)

# LINE 聊天機器人的基本資料
line_bot_api = LineBotApi('rtut2oGaCBibk5DTObwKuFgQgD8rC7JazGdF9f68BIP/2lXU+bBWjm3JgHQtvh0iHySthUi2We1XPVlGTMCh9s8Q1IZZL58osZBRvyHz8GXOnp4cd959MMyh/bXZkpaqdOepM0vcrSXXZvHSzcolLQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('5fecbae22c9e1492decda139bd70fd70')
parser = WebhookParser('5fecbae22c9e1492decda139bd70fd70')

# 打個招呼 :)
@app.route("/", methods=['GET'])
def hello():
    return "Hi! Wanna find some InTeREsTInG books?"

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

#----------------設定回覆訊息介面-----------------
@handler.add(MessageEvent, message=TextMessage)
def test1(event):
    #----------------取得userid-----------------
    user_id = event.source.user_id
    if user_id == '':
        user_id = event.source.user_id  
    #----------------地區-----------------
    TWregion = ["北部","中部","南部","東部"]
    city_name = ["台北市","新北市","基隆市","桃園市","苗栗縣","新竹縣","新竹市","台中市","彰化縣","南投縣","雲林縣","嘉義市","台南市","高雄市","屏東縣","宜蘭縣","花蓮縣","台東縣", "金門縣, 連江縣, 澎湖縣"]
    city_name_dic = {**n_dict, **c_dict, **s_dict, **e_dict}
    city_region_dict = dict(zip(["north","center","south","east"], [north,center,south,east]))
    
    #----------------選擇縣市介面-----------------
    if event.message.text == "選擇縣市":
        flex_message0 = flex_template.main_panel_flex()
        line_bot_api.reply_message(event.reply_token,flex_message0)
    #----------------不同區域的介面設定-----------------
    elif event.message.text in TWregion:
            #讀需要的json資料
        f_region = open('json_files_for_robot/json_for_app.json', encoding="utf8") 
        data_region = json.load(f_region) 

        for i,v in enumerate(TWregion):
            if event.message.text == v:
                flex_message1 = FlexSendMessage(
                               alt_text= v + '的縣市',
                               contents= data_region[i]
                )

                line_bot_api.reply_message(event.reply_token,flex_message1) 

        f_region.close()
    
    #----------------爬蟲----------------- 
    else: 
        worksheet.clear()
        str_input = event.message.text.split(' ')
        ISBN = str_input[0]
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit?usp=sharing")
        )

        NTCs = ["ntc", "NTC", "國立臺東專科學校", "臺東專科學校", "東專", "台東專科學校", "國立台東專科學校"]
        HWUs = ["hwu","HWU", "醒吾科技大學", "醒吾科大", "醒吾"]
        ILCCBs = ["ilccb","ILCCB","宜蘭縣公共圖書館","宜蘭縣圖書館","宜蘭圖書館" "宜蘭縣圖","宜圖"]
        YLCCBs = ["ylccb","YLCCB","雲林縣公共圖書館","雲林縣圖書館","雲林圖書館" "雲林縣圖","雲圖"]
        TYPLs = ["typl","TYPL","桃園市立圖書館","桃園市圖書館","桃園圖書館" "桃園市圖","桃圖"]
        KSMLs = ["ksml","KSML","高雄市立圖書館","高雄市圖書館","高雄圖書館" "高雄市圖","高圖"]
        PTPLs = ["ptpl","PTPL","屏東縣公共圖書館","屏東縣圖書館","屏東圖書館" "屏東縣圖","屏圖"]

        FGUs = ["fgu","FGU", "佛光大學", "佛光", "佛大"]
        NIUs = ["niu","NIU", "國立宜蘭大學", "宜蘭大學", "宜大", "宜蘭大"]
        CUSTs = ["cust","CUST", "中華科技大學", "中華科大"]
        CNUs = ["cnu", "CNU", "嘉南藥理大學", "嘉藥"]
        TPMLs = ["tpml","TPML", "臺北市立圖書館", "台北市立圖書館", "北市圖"]  
        NTUAs = ["NTUA","ntua", "國立臺灣藝術大學","國立台灣藝術大學", "臺灣藝術大學", "台灣藝術大學", "臺藝大", "台藝大"]      
        UTaipeis = ["UTaipei", "臺北市立大學", "台北市立大學", "臺北市大", "台北市大", "北市大"]
        NTUTs = ["ntut","NTUT", "國立臺北科技大學", "國立台北科技大學", "臺北科技大學", "台北科技大學", "臺北科大", "台北科大", "北科大", "北科"]
        TMUs = ["tmu","TMU","臺北醫學大學","台北醫學大學","北醫"]
        NTUBs = ["ntub","NTUB", "國立臺北商業大學", "國立台北商業大學", "臺北商業大學", "台北商業大學", "臺北商大", "台北商大", "北商大", "北商"]
        Miaolis = ["Miaoli","miaoli","苗栗縣立圖書館","苗栗縣公共圖書館","苗栗縣圖書館", "苗栗縣圖", "苗栗圖書館", "苗栗"]
        JUSTs = ["just","JUST", "景文科技大學", "景文科大", "景文"]
        CLUTs = ["clut","CLUT", "致理科技大學", "致理科大", "致理"]
        VNUs = ["vnu","VNU", "萬能科技大學", "萬能科大", "萬能"]
        UCHs = ["uch","UCH", "健行科技大學", "健行科大", "健行"]
        MUSTs = ["must","MUST", "明新科技大學", "明新科大", "明新"]
        YDUs = ["ydu","YDU", "育達科技大學", "育達科大", "育達"]
        CUTEs = ["cute","CUTE", "中國科技大學", "中國科大"]
        NTCUs = ["ntcu","NTCU", "國立臺中教育大學", "國立台中教育大學", "臺中教育大學", "台中教育大學", "中教大", "中教"]
        NTUSs = ["ntus","NTUS", "國立臺灣體育運動大學","國立台灣體育運動大學","臺灣體育運動大學","台灣體育運動大學","臺體大","台體大","臺體","台體"]
        THUs = ["thu","THU", "東海大學", "東海"]
        PUs = ["pu","PU", "靜宜大學", "靜宜"]
        OCUs = ["ocu","OCU", "僑光科技大學", "僑光科大", "僑光"]
        NCUEs = ["ncue","NCUE", "國立彰化師範大學","彰化師範大學","彰化師大","彰師大"]


        NDHUs = ["ndhu","NDHU", "國立東華大學", "東華大學","東華"]
        NTOUs = ["ntou","NTOU", "國立臺灣海洋大學", "國立台灣海洋大學", "海大", "海洋大學"]
        NTNUs = ["ntnu","NTNU", "國立臺灣師範大學","國立台灣師範大學","臺灣師範大學","台灣師範大學","台師大","臺師大", "台師", "臺師"]
        NTUSTs = ["ntust","NTUST", "國立臺灣科技大學","國立台灣科技大學","臺灣科技大學","台灣科技大學","臺灣科大","台灣科大","台科大","臺科大","臺科","台科"]
        CYCUs = ["cycu","CYCU", "中原大學", "中原"]
        FCUs = ["fcu","FCU", "逢甲大學", "逢甲", "逢大"]
        CYUTs = ["cyut","CYUT", "朝陽科技大學", "朝陽科大", "朝陽"]
        NSYSUs = ["nsysu","NSYSU", "國立中山大學", "中山大學","中山大", "中山"]
        NKNUs = ["nknu","NKNU", "國立高雄師範大學", "高雄師範大學", "高師大", "高師"]
        WZUs = ["wzu","WZU", "文藻外語大學", "文藻外語大","文藻外大", "文藻"]
        Tajens = ["tajen","Tajen", "大仁科技大學", "大仁科大", "大仁"]
        NCUs = ["ncu","NCU", "國立中央大學", "中央大學", "中央", "中大"]
        PCCUs = ["pccu","PCCU", "中國文化大學", "文化大學","文化", "文大"]
        FJUs = ["fju", "FJU", "輔仁大學", "輔仁", "輔大"]
        SINICAs = ["sinica","SINICA", "中央研究院", "中研院"]
        NYCUs = ["nycu","NYCU", "國立陽明交通大學","陽明交通大學", "陽明交通", "陽交大", "陽交"]        
        NTPCs = ["ntpc","NTPC", "新北市立圖書館", "新北市圖","新北市圖書館"]
        KLCCABs = ["klccab","KLCCAB","kllib","KLLIB","基隆市公共圖書館","基隆市圖","基隆市圖書館", "基隆圖書館"]
        
        
        NCLs = ["ncl","NCL", "國家圖書館", "國圖"]
        NTUs = ["ntu","NTU", "國立臺灣大學", "國立台灣大學", "臺灣大學", "台灣大學", "臺大", "台大"]
        NCCUs = ["nccu","NCCU", "國立政治大學", "政治大學", "政大"]
        CGUs = ["cgu","CGU", "長庚大學", "長庚"]

        MMCs = ["mmc","MMC", "馬偕醫學院", "馬偕醫", "馬偕"]
        ITRIs = ["itri","ITRI", "工業技術研究院", "工研院"]
        

        for i in range(1, len(str_input)):
            if str_input[i] in NTCs: # 國立臺東專科學校              
                NTC(ISBN)
            elif str_input[i] in HWUs: # 醒吾科技大學
                HWU(ISBN)                       
            elif str_input[i] in ILCCBs: # 宜蘭縣公共圖書館
                ILCCB(ISBN)
            elif str_input[i] in TYPLs: # 桃園市立圖書館
                TYPL(ISBN)
            elif str_input[i] in KSMLs: # 高雄市立圖書館
                KSML(ISBN)
            elif str_input[i] in PTPLs: # 屏東縣公共圖書館
                PTPL(ISBN)



            elif str_input[i] in FGUs: # 佛光大學
                FGU(ISBN)
            elif str_input[i] in NIUs: # 國立宜蘭大學
                NIU(ISBN)  
            elif str_input[i] in CUSTs: # 中華科技大學
                CUST(ISBN)  
            elif str_input[i] in CNUs: # 嘉南藥理大學
                CNU(ISBN)  
            elif str_input[i] in TPMLs: # 臺北市立圖書館
                TPML(ISBN)    
            elif str_input[i] in NTUAs: # 國立臺灣藝術大學
                NTUA(ISBN) 
            elif str_input[i] in UTaipeis: # 臺北市立大學
                UTaipei(ISBN) 
            elif str_input[i] in NTUTs: # 國立臺北科技大學
                NTUT(ISBN) 
            elif str_input[i] in TMUs: # 臺北醫學大學
                TMU(ISBN) 
            elif str_input[i] in NTUBs: # 國立臺北商業大學
                NTUB(ISBN) 
            elif str_input[i] in Miaolis: # 苗栗縣立圖書館
                Miaoli(ISBN) 
            elif str_input[i] in JUSTs: # 景文科技大學
                JUST(ISBN) 
            elif str_input[i] in CLUTs: # 致理科技大學
                CLUT(ISBN)             
            elif str_input[i] in VNUs: # 萬能科技大學
                VNU(ISBN)
            elif str_input[i] in UCHs: # 健行科技大學
                UCH(ISBN)
            elif str_input[i] in MUSTs: # 明新科技大學
                MUST(ISBN)
            elif str_input[i] in YDUs: # 育達科技大學
                YDU(ISBN)
            elif str_input[i] in CUTEs: # 中國科技大學
                CUTE(ISBN)
            elif str_input[i] in NTCUs: # 國立臺中教育大學
                NTCU(ISBN)
            elif str_input[i] in NTUSs: # 國立臺灣體育運動大學
                NTUS(ISBN)
            elif str_input[i] in THUs: # 東海大學
                THU(ISBN)
            elif str_input[i] in PUs: # 靜宜大學
                PU(ISBN)
            elif str_input[i] in OCUs: # 僑光科技大學
                OCU(ISBN)
            elif str_input[i] in NCUEs: # 國立彰化師範大學
                NCUE(ISBN)
            elif str_input[i] in YLCCBs: # 雲林縣公共圖書館
                YLCCB(ISBN)


            elif str_input[i] in NTOUs: # 國立臺灣海洋大學
                NTOU(ISBN)                 
            elif str_input[i] in NTUSTs: # 國立臺灣科技大學
                NTUST(ISBN)
            elif str_input[i] in NTNUs: # 國立臺灣師範大學
                NTNU(ISBN)  
            elif str_input[i] in CYCUs: # 中原大學
                CYCU(ISBN)
            elif str_input[i] in FCUs: # 逢甲大學
                FCU(ISBN) 
            elif str_input[i] in CYUTs: # 朝陽科技大學
                CYUT(ISBN)
            elif str_input[i] in NSYSUs: # 國立中山大學
                NSYSU(ISBN)
            elif str_input[i] in NKNUs: # 國立高雄師範大學
                NKNU(ISBN)
            elif str_input[i] in WZUs: # 文藻外語大學
                WZU(ISBN)
            elif str_input[i] in Tajens: # 大仁科技大學
                Tajen(ISBN)
            elif str_input[i] in NCUs: # 國立中央大學
                NCU(ISBN)
            elif str_input[i] in SINICAs: # 中央研究院
                SINICA(ISBN) 
            elif str_input[i] in PCCUs: # 中國文化大學
                PCCU(ISBN)                 
            elif str_input[i] in FJUs: # 輔仁大學
                FJU(ISBN)  
            elif str_input[i] in NYCUs: # 國立陽明交通大學
                NYCU(ISBN)
            elif str_input[i] in NTPCs: # 新北市立圖書館
                NTPC(ISBN) 
            elif str_input[i] in KLCCABs: # 基隆市公共圖書館
                KLCCAB(ISBN)

            elif str_input[i] in NCLs: # 國家圖書館
                NCL(ISBN)
            elif str_input[i] in NTUs: # 國立臺灣大學
                NTU(ISBN)
            elif str_input[i] in NCCUs: # 國立政治大學
                NCCU(ISBN)
            elif str_input[i] in CGUs: # 長庚大學
                CGU(ISBN)
            elif str_input[i] in MMCs: # 馬偕醫學院
                MMC(ISBN)
            elif str_input[i] in ITRIs: # 工業技術研究院
                ITRI(ISBN)
            else:
                print("nono")
            

    

if __name__ == "__main__":
    app.run(debug=True)