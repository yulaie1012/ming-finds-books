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
'''
from google.oauth2 import service_account
from google.oauth2.service_account import Credentials
import gspread
import gspread_dataframe as gd
'''
#---------------------------------------
import import_ipynb
import toread
from toread import toread, toread_crawlers, NTC, HWU
import INSTs
'''
from INSTs import organize_columns, wait_for_element_present, wait_for_url_changed, accurately_find_table_and_read_it, \
    search_ISBN, click_more_btn, TPML, webpac_jsp_crawler, FGU, select_ISBN_strategy, NTOU, \
    easy_crawler, NYCU, NTNU, NTUST, PCCU, FJU, SINICA, webpac_pro_crawler, webpac_ajax_crawler, NTPC, KLCCAB, \
    基隆市公共圖書館, webpac_gov_crawler, ILCCB, wait_for_element_clickable, NIU, 國家圖書館, NCL, CYCU, \
    primo_crawler, NTU, NCCU, primo_greendot_crawler, CGU, primo_greendot_finding, primo_finding, CYUT, \
    FCU, NSYSU, NKNU, WZU, Tajen, NCU, CUST, CNU, NTUA, UTaipei, NTUT, TMU, NTUB, Miaoli, JUST, CLUT, VNU, UCH, \
    MUST, YDU, CUTE, MMC, ITRI, NTCU, NTUS, THU, PU, OCU, NCUE, YLCCB, TYPL, KSML, PTPL, CYCPL, NHU, FEU, CSU, \
    Meiho, OUK, NPTU, webpac_aspx_crawler, TSU, STU, KSU, NTUNHS, uhtbin_crawler, TTU, NTSU, ugly_crawler, \
    Matsu, KNU, toread_crawler, CHPL, KMU, NFU, NPUST, NKUHT, primo_two_crawler, TKU, MCU, SCU, CCU, CJCU, \
    世新大學, SHU, 台北海洋科技大學, TUMT, webpac_two_cralwer, TNUA, NCUT, ISU, CSMU, NHRI, HKU, HUST, HWH, \
    wait_for_elements_present, primo_two_finding, CKU, CCT, HDUT, NOU, Jente, NTTU, NQU, NKUST, HLPL, NYUST, \
    TFAI, AU, USC, HFU, NUU, PHPL, SJU, TNU, YPU, LTU, CTU, NKUT, MDU, DYU, HSC, CJC, NDHU, NUK, MCUT, CGUST, \
    NTHU, NCNU, NUTN, TPCU, webpac_cfm_crawler, NTPU, TMUST, LHU, TCPL, CMU, Asia, TNPL, TCU, NPU, KMCPL, TTCPL, \
    HCLIB, CYLIB, HCPL, NTCH, NMP, TGST, NTMOFA, KYU, chungchung_crawler, CTUST, CCUST, crawl_all_tables_on_page, \
    get_all_tgt_urls, 國立臺中科技大學, NUTC, 敏實科技大學, MITUST
'''
from INSTs import organize_columns, wait_for_element_present, wait_for_url_changed, accurately_find_table_and_read_it, \
    search_ISBN, click_more_btn, webpac_jsp_crawler, FGU, select_ISBN_strategy, wait_for_element_clickable

'''
scope = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_service_account_file("json_files_for_robot/books-319701-17701ae5510b.json", scopes=scope)
gs = gspread.authorize(creds)
sheet = gs.open_by_url('https://docs.google.com/spreadsheets/d/17fJuHSGHnjHbyKJzTgzKpp1pe2J6sirK5QVjg2-8fFo/edit#gid=0')
worksheet = sheet.get_worksheet(0)
'''

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
# line_bot_api = LineBotApi(os.environ['CHANNEL_ACCESS_TOKEN'])
# handler = WebhookHandler(os.environ['CHANNEL_SECRET'])
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
        TYPLs = ["typl","TYPL","桃園市立圖書館","桃園市圖書館","桃園圖書館" "桃園市圖","桃圖"]
        KSMLs = ["ksml","KSML","高雄市立圖書館","高雄市圖書館","高雄圖書館" "高雄市圖","高圖"]
        PTPLs = ["ptpl","PTPL","屏東縣公共圖書館","屏東縣圖書館","屏東圖書館" "屏東縣圖","屏圖"]
        HLPLs = ["hlpl","HLPL","花蓮縣公共圖書館","花蓮縣圖書館","花蓮圖書館" "花蓮縣圖","花圖"]
        PHPLs = ["phpl","PHPL","phlib","澎湖縣公共圖書館","澎湖縣圖書館","澎湖圖書館" "澎湖縣圖","澎圖"]
        NYUSTs = ["nyust","NYUST", "國立雲林科技大學", "雲林科技大學", "雲林科大", "雲科大", "雲科"]
        TFAIs = ["tfai","TFAI","國家電影及視聽文化中心", "國家影視聽中心", "國家電影中心", "影視聽中心"]

        FGUs = ["fgu","FGU", "佛光大學", "佛光", "佛大"]
        CKUs = ["cku","CKU", "經國管理暨健康學院", "經國學院"]
        NIUs = ["niu","NIU", "國立宜蘭大學", "宜蘭大學", "宜大", "宜蘭大"]
        CUSTs = ["cust","CUST", "中華科技大學", "中華科大"]
        CCTs = ["cct","CCT", "臺北基督學院", "台北基督學院"]
        HDUTs = ["hdut","HDUT", "宏國德霖科技大學", "宏國德霖科大", "宏國德霖"]
        CNUs = ["cnu", "CNU", "嘉南藥理大學", "嘉藥"]
        TPMLs = ["tpml","TPML", "臺北市立圖書館", "台北市立圖書館", "臺北市圖書館", "台北市圖書館", "臺北市圖", "台北市圖", "北市圖", "北圖"]  
        NTUAs = ["NTUA","ntua", "國立臺灣藝術大學","國立台灣藝術大學", "臺灣藝術大學", "台灣藝術大學", "臺藝大", "台藝大", "臺藝", "台藝"]      
        UTaipeis = ["UTaipei", "臺北市立大學", "台北市立大學", "臺北市大", "台北市大", "北市大"]
        NTUTs = ["ntut","NTUT", "國立臺北科技大學", "國立台北科技大學", "臺北科技大學", "台北科技大學", "臺北科大", "台北科大", "北科大", "北科"]
        TMUs = ["tmu","TMU","臺北醫學大學","台北醫學大學","北醫"]
        NTUBs = ["ntub","NTUB", "國立臺北商業大學", "國立台北商業大學", "臺北商業大學", "台北商業大學", "臺北商大", "台北商大", "北商大", "北商"]
        HCLIBs = ["hclib","HCLIB", "新竹市文化局圖書館", "新竹市立圖書館", "新竹市圖書館", "新竹市圖", "竹市圖"]
        HCPLs = ["hcpl","HCPL", "新竹縣公共圖書館", "新竹縣立圖書館", "新竹縣圖書館", "新竹縣圖", "竹縣圖"]
        Miaolis = ["Miaoli","miaoli","苗栗縣立圖書館","苗栗縣公共圖書館","苗栗縣圖書館", "苗栗縣圖", "苗栗圖書館", "苗栗"]
        JUSTs = ["just","JUST", "景文科技大學", "景文科大", "景文"]
        CLUTs = ["clut","CLUT", "致理科技大學", "致理科大", "致理"]
        VNUs = ["vnu","VNU", "萬能科技大學", "萬能科大", "萬能"]
        UCHs = ["uch","UCH", "健行科技大學", "健行科大", "健行"]
        MUSTs = ["must","MUST", "明新科技大學", "明新科大", "明新"]
        NOUs = ["nou","NOU", "國立空中大學", "空中大學", "空大"]
        YDUs = ["ydu","YDU", "育達科技大學", "育達科大", "育達"]
        Jentes = ["jente","Jente","JENTE", "仁德醫護管理專科學校", "仁德醫護", "仁德醫專"]
        CUTEs = ["cute","CUTE", "中國科技大學", "中國科大"]
        NTCUs = ["ntcu","NTCU", "國立臺中教育大學", "國立台中教育大學", "臺中教育大學", "台中教育大學", "中教大", "中教"]
        NTUSs = ["ntus","NTUS", "國立臺灣體育運動大學","國立台灣體育運動大學","臺灣體育運動大學","台灣體育運動大學","臺體大","台體大","臺體","台體"]
        THUs = ["thu","THU", "東海大學", "東海"]
        PUs = ["pu","PU", "靜宜大學", "靜宜"]
        OCUs = ["ocu","OCU", "僑光科技大學", "僑光科大", "僑光"]
        NCUEs = ["ncue","NCUE", "國立彰化師範大學","彰化師範大學","彰化師大","彰師大"]
        YLCCBs = ["ylccb","YLCCB","雲林縣公共圖書館","雲林縣圖書館","雲林圖書館" "雲林縣圖","雲圖"]
        CYLIBs = ["cylib","CYLIB", "嘉義市文化局圖書館", "嘉義市立圖書館", "嘉義市圖書館", "嘉義市圖", "嘉市圖"]
        CYCPLs = ["cycpl","cypl","CYCPL","CYPL","嘉義縣圖書館","嘉義縣圖書館","嘉義圖書館", "嘉義縣圖", "嘉縣圖"]
        NHUs = ["nhu","NHU", "南華大學", "南華"]
        FEUs = ["feu","FEU", "遠東科技大學", "遠東科大", "遠東"]
        CSUs = ["csu","CSU", "正修科技大學", "正修科大", "正修"]
        Meihos = ["meiho","Meiho", "美和科技大學", "美和科大", "美和"]
        NTTUs = ["nttu","NTTU", "國立臺東大學", "國立台東大學", "臺東大學", "台東大學", "臺東大", "台東大", "東大"]
        TTCPLs = ["ttcpl","TTCPL", "臺東縣立圖書館", "臺東縣圖書館","臺東圖書館", "臺東縣圖", "東圖"]
        NQUs = ["nqu","NQU", "國立金門大學", "金門大學", "金大"]
        KMCPLs = ["kmcpl","KMCPL", "金門縣立圖書館", "金門縣圖書館", "金門圖書館", "金門縣圖", "金圖"]
        
        NTOUs = ["ntou","NTOU", "國立臺灣海洋大學", "國立台灣海洋大學", "海大", "海洋大學"]
        NTNUs = ["ntnu","NTNU", "國立臺灣師範大學","國立台灣師範大學","臺灣師範大學","台灣師範大學","台師大","臺師大", "台師", "臺師"]
        NTUSTs = ["ntust","NTUST", "國立臺灣科技大學","國立台灣科技大學","臺灣科技大學","台灣科技大學","臺灣科大","台灣科大","台科大","臺科大","臺科","台科"]
        CYCUs = ["cycu","CYCU", "中原大學", "中原"]
        FCUs = ["fcu","FCU", "逢甲大學", "逢甲", "逢大"]
        CYUTs = ["cyut","CYUT", "朝陽科技大學", "朝陽科大", "朝陽"]
        NSYSUs = ["nsysu","NSYSU", "國立中山大學", "中山大學","中山大", "中山"]
        NKNUs = ["nknu","NKNU", "國立高雄師範大學", "高雄師範大學", "高師大", "高師"]
        WZUs = ["wzu","WZU", "文藻外語大學", "文藻外語大","文藻外大", "文藻"]
        Tajens = ["tj","TJ","tajen","Tajen", "大仁科技大學", "大仁科大", "大仁"]
        NCUs = ["ncu","NCU", "國立中央大學", "中央大學", "中央", "中大"]
        PCCUs = ["pccu","PCCU", "中國文化大學", "文化大學","文化", "文大"]
        FJUs = ["fju", "FJU", "輔仁大學", "輔仁", "輔大"]
        SINICAs = ["sinica","SINICA", "中央研究院", "中研院"]
        NYCUs = ["nycu","NYCU", "國立陽明交通大學","陽明交通大學", "陽明交通", "陽交大", "陽交"]        
        NTPCs = ["ntpc","NTPC", "新北市立圖書館", "新北市圖","新北市圖書館"]
        OUKs = ["ouk","OUK", "高雄市立空中大學", "高雄空大", "高空大", "市立空大"]
        NPTUs = ["nptu","NPTU", "國立屏東大學", "屏東大學", "屏大", "屏東大"]
        STUs = ["stu","STU", "樹德科技大學", "樹德科大", "樹德"]
        TSUs = ["TSU", "臺灣首府大學", "台灣首府大學", "首府大學", "首府大", "台首大", "臺首大"]
        KSUs = ["ksu","KSU", "崑山科技大學", "崑山科大", "崑山"]
        HKUs = ["hku","HKU", "弘光科技大學", "弘光科大", "弘光"]
        HUSTs = ["hust","HUST", "修平科技大學", "修平科大", "修平"]
        HWHs = ["hwh","HWH", "華夏科技大學", "華夏科大", "華夏"]
        AUs = ["au","AU", "真理大學", "真理"]
        USCs = ["usc","USC", "實踐大學", "實踐大", "實踐", "實大"]
        HFUs = ["hfu","HFU", "華梵大學", "華梵大", "華梵"]
        NUUs = ["nuu","NUU", "國立聯合大學", "聯合大學", "聯合大", "聯合", "聯大"]

        NTUNHSs = ["ntunhs","NTUNHS", "國立臺北護理健康大學", "國立台北護理健康大學", "北護大", "國北護", "北護"]
        TTUs = ["ttu","TTU", "大同大學", "大同"]
        NTSUs = ["ntsu","NTSU", "國立體育大學", "國體大", "國體"]
        Matsus = ["matsu","Matsu","連江縣公共圖書館","連江縣圖書館","連江圖書館" "連江縣圖", "馬祖"]
        KNUs = ["knu","KNU", "開南大學", "開南", "開大"]
        CHPLs = ["chpl","CHPL","彰化縣公共圖書館","彰化縣圖書館","彰化圖書館" "彰化縣圖","彰圖"]
        KMUs = ["kmu","KMU", "高雄醫學大學", "高雄醫大", "高醫"]
        NFUs = ["nfu","NFU", "國立虎尾科技大學", "虎尾科技大學", "虎尾科大", "虎科大", "虎尾", "虎科"]
        SJUs = ["sju","SJU", "聖約翰科技大學", "聖約翰科大", "聖約翰"]
        TNUs = ["tnu","TNU", "東南科技大學", "東南科大", "東南"]
        HSCs = ["hsc","HSC", "新生醫護管理專科學校", "新生醫專", "新生醫護", "新生護專", "新生專校"]
        CJCs = ["hsc","CJC", "崇仁醫護管理專科學校", "崇仁醫專", "崇仁醫護", "崇仁護專", "崇仁專校"]
        YPUs = ["ypu","YPU", "元培醫事科技大學", "元培醫事科大", "元培醫事", "元培"]
        LTUs = ["ltu","LTU", "嶺東科技大學", "嶺東科大", "嶺東"]
        MDUs = ["mdu","MDU", "明道大學", "明道大", "明道", "明大"]
        DYUs = ["dyu","DYU", "大葉大學", "大葉大", "大葉"]
        CTUs = ["ctu","CTU", "建國科技大學", "建國科大", "建國"]
        NKUTs = ["nkut","NKUT", "南開科技大學", "南開科大", "南開"]
        NUKs = ["nuk","NUK", "國立高雄大學", "高雄大學", "高雄大", "高大"]
        NDHUs = ["ndhu","NDHU", "國立東華大學", "東華大學","東華"]

        TNUAs = ["TNUA","tnua", "國立臺北藝術大學","國立台北藝術大學", "臺北藝術大學", "台北藝術大學", "北藝大", "北藝"]
        NCUTs = ["ncut","NCUT", "國立勤益科技大學", "勤益科技大學", "勤益科大", "勤科大", "勤科"]
        ISUs = ["isu","ISU", "義守大學", "義守", "義大"]
        CSMUs = ["csmu","CSMU", "中山醫學大學", "中山醫大", "中山醫"]
        NHRIs = ["nhri","NHRI", "國家衛生研究院", "國衛院"]

        TPCUs = ["tpcu","TPCU", "臺北城市科技大學","台北城市科技大學","城市科技大學","北城科大","城市科大","城科大","城科","城大","北城"]
        NTPUs = ["ntpu","NTPU", "國立臺北大學", "國立台北大學", "臺北大學", "台北大學", "臺北大", "台北大", "北大"]
        TMUSTs = ["tmust","TMUST", "德明財經科技大學", "德明科大", "德明"]
        LHUs = ["lhu","LHU", "龍華科技大學", "龍華科大", "龍華"]
        TCPLs = ["tcpl","TCPL","臺中市立圖書館","台中市立圖書館","臺中市圖書館","台中市圖書館","臺中圖書館","台中圖書館","臺中市圖","台中市圖","中圖"]
        CMUs = ["cmu","CMU", "中國醫藥大學", "中國醫"]
        Asias = ["asia","Asia", "亞洲大學", "亞洲大", "亞洲", "亞洲大"]
        TNPLs = ["tnpl","TNPL", "臺南市立圖書館", "台南市立圖書館", "臺南市圖書館", "台南市圖書館", "臺南市圖", "台南市圖", "南圖"]
        TCUs = ["tcu","TCU", "慈濟大學", "慈濟", "慈大"]
        NPUs = ["npu","NPU", "國立澎湖科技大學", "澎湖科技大學", "澎湖科大", "澎科大", "澎科"]

        KLCCABs = ["klccab","KLCCAB","kllib","KLLIB","基隆市公共圖書館","基隆市圖","基隆市圖書館", "基隆圖書館"]
        NUTCs = ["nutc","NUTC", "國立臺中科技大學","國立台中科技大學","臺中科技大學","台中科技大學","臺中科大","台中科大","中科大","中科"]
        NCLs = ["ncl","NCL", "國家圖書館", "國圖"]
        SHUs = ["shu","SHU", "世新大學", "世新"]
        TUMTs = ["tumt","TUMT", "臺北海洋科技大學", "台北海洋科技大學", "北海科大"]
        MITUSTs = ["mitust","MITUST", "敏實科技大學", "敏實科大", "敏實"]

        NTUs = ["ntu","NTU", "國立臺灣大學", "國立台灣大學", "臺灣大學", "台灣大學", "臺大", "台大"]
        NCCUs = ["nccu","NCCU", "國立政治大學", "政治大學", "政大"]
        TKUs = ["tku","TKU", "淡江大學", "淡江", "淡大"]
        MCUs = ["mcu","MCU", "銘傳大學", "銘傳"]
        SCUs = ["scu","SCU", "東吳大學", "東吳"]
        NKUSTs = ["nkust","NKUST", "國立高雄科技大學", "高雄科技大學", "高雄科大", "高科大", "高科"]
        NPUSTs = ["npust","NPUST", "國立屏東科技大學", "屏東科技大學", "屏東科大", "屏科大", "屏科"]
        NKUHTs = ["nkuht","NKUHT", "國立高雄餐旅大學", "高雄餐旅大學", "高餐大", "高餐"]
        CGUs = ["cgu","CGU", "長庚大學", "長庚"]
        CCUs = ["ccu","CCU", "國立中正大學", "中正大學", "中正大", "中正"]
        CJCUs = ["cjcu","CJCU", "長榮大學", "長榮", "長榮大"]

        MMCs = ["mmc","MMC", "馬偕醫學院", "馬偕醫", "馬偕"]
        ITRIs = ["itri","ITRI", "工業技術研究院", "工研院"]
        MCUTs = ["mcut","MCUT", "明志科技大學", "明志科大", "明志"]
        CGUSTs = ["cgust","CGUST", "長庚科技大學", "長庚科大"]
        NTHUs = ["nthu","NTHU", "國立清華大學", "清華大學", "清華大", "清華", "清大"]
        NCNUs = ["ncnu","NCNU","國立暨南國際大學", "暨南國際大學","暨南大學", "暨大"]
        NUTNs = ["nutn","NUTN", "國立臺南大學", "國立台南大學", "臺南大學", "台南大學", "臺南大", "台南大", "南大"]
        NTCHs = ["ntch","NTCH", "國家兩廳院", "兩廳院"]
        NMPs = ["nmp","NMP","國立臺灣史前文化博物館","國立台灣史前文化博物館","臺灣史前文化博物館","台灣史前文化博物館","史前文化博物館","史前館"]
        TGSTs = ["tgst","TGST", "台灣神學研究學院", "台灣神學院", "台神研", "台神"]
        NTMOFAs = ["ntmpfa","NTMOFA", "國立臺灣美術館", "國立台灣美術館", "國美館"]
        KYUs = ["kyu","KYU", "高苑科技大學", "高苑科大", "高苑"]
        CTUSTs = ["ctust","CTUST", "中臺科技大學", "中台科技大學", "中臺科大", "中台科大", "中臺", "中台"]
        CCUSTs = ["ccust","CCUST", "中州科技大學", "中州科大", "中州"]

        
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
            elif str_input[i] in HLPLs: # 花蓮縣公共圖書館
                HLPL(ISBN)
            elif str_input[i] in PHPLs: # 澎湖縣公共圖書館
                PHPL(ISBN)
            elif str_input[i] in NYUSTs: # 國立雲林科技大學
                NYUST(ISBN)
            elif str_input[i] in TFAIs: # 國家電影及視聽文化中心
                TFAI(ISBN)                                                                

            elif str_input[i] in FGUs: # 佛光大學
                FGU(ISBN)
            elif str_input[i] in CKUs: # 經國管理暨健康學院
                CKU(ISBN)                
            elif str_input[i] in NIUs: # 國立宜蘭大學
                NIU(ISBN)  
            elif str_input[i] in CUSTs: # 中華科技大學
                CUST(ISBN)
            elif str_input[i] in CCTs: # 臺北基督學院
                CCT(ISBN)  
            elif str_input[i] in HDUTs: # 宏國德霖科技大學
                HDUT(ISBN)                  

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
            elif str_input[i] in HCLIBs: # 新竹市立圖書館
                HCLIB(ISBN) 
            elif str_input[i] in HCPLs: # 新竹縣公共圖書館
                HCPL(ISBN)                                 
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
            elif str_input[i] in NOUs: # 國立空中大學
                NOU(ISBN)                
            elif str_input[i] in YDUs: # 育達科技大學
                YDU(ISBN)
            elif str_input[i] in Jentes: # 仁德醫護管理專科學校
                Jente(ISBN)                
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
            elif str_input[i] in CYLIBs: # 嘉義市立圖書館
                CYLIB(ISBN)                 
            elif str_input[i] in CYCPLs: # 嘉義縣圖書館
                CYCPL(ISBN)
            elif str_input[i] in NHUs: # 南華大學
                NHU(ISBN)
            elif str_input[i] in FEUs: # 遠東科技大學
                FEU(ISBN)
            elif str_input[i] in CSUs: # 正修科技大學
                CSU(ISBN)
            elif str_input[i] in Meihos: # 美和科技大學
                Meiho(ISBN)
            elif str_input[i] in NTTUs: # 國立臺東大學
                NTTU(ISBN)
            elif str_input[i] in TTCPLs: # 臺東縣立圖書館
                TTCPL(ISBN)                    
            elif str_input[i] in NQUs: # 國立金門大學
                NQU(ISBN)
            elif str_input[i] in KMCPLs: # 金門縣立圖書館
                KMCPL(ISBN)                                                                

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
            elif str_input[i] in OUKs: # 高雄市立空中大學
                OUK(ISBN) 
            elif str_input[i] in NPTUs: # 國立屏東大學
                NPTU(ISBN) 
            elif str_input[i] in STUs: # 樹德科技大學
                STU(ISBN) 
            elif str_input[i] in TSUs: # 台灣首府大學
                TSU(ISBN) 
            elif str_input[i] in KSUs: # 崑山科技大學
                KSU(ISBN) 
            elif str_input[i] in HKUs: # 弘光科技大學
                HKU(ISBN) 
            elif str_input[i] in HUSTs: # 修平科技大學
                HUST(ISBN) 
            elif str_input[i] in HWHs: # 華夏科技大學
                HWH(ISBN)                     
            elif str_input[i] in AUs: # 真理大學
                AU(ISBN)                   
            elif str_input[i] in USCs: # 實踐大學
                USC(ISBN)                   
            elif str_input[i] in HFUs: # 華梵大學
                HFU(ISBN)   
            elif str_input[i] in NUUs: # 國立聯合大學
                NUU(ISBN)                                                                   

            elif str_input[i] in NTUNHSs: # 國立臺北護理健康大學
                NTUNHS(ISBN) 
            elif str_input[i] in TTUs: # 大同大學
                TTU(ISBN) 
            elif str_input[i] in NTSUs: # 國立體育大學
                NTSU(ISBN)                                 
            elif str_input[i] in Matsus: # 連江縣公共圖書館
                Matsu(ISBN)  
            elif str_input[i] in KNUs: # 開南大學
                KNU(ISBN)  
            elif str_input[i] in CHPLs: # 彰化縣公共圖書館
                CHPL(ISBN)  
            elif str_input[i] in KMUs: # 高雄醫學大學
                KMU(ISBN)  
            elif str_input[i] in NFUs: # 國立虎尾科技大學
                NFU(ISBN)  
            elif str_input[i] in SJUs: # 聖約翰科技大學
                SJU(ISBN)  
            elif str_input[i] in TNUs: # 東南科技大學
                TNU(ISBN)  
            elif str_input[i] in HSCs: # 新生醫護管理專科學校
                HSC(ISBN)
            elif str_input[i] in CJCs: # 崇仁醫護管理專科學校
                CJC(ISBN)                                     
            elif str_input[i] in YPUs: # 元培醫事科技大學
                YPU(ISBN)  
            elif str_input[i] in LTUs: # 嶺東科技大學
                LTU(ISBN)
            elif str_input[i] in MDUs: # 明道大學
                MDU(ISBN)   
            elif str_input[i] in DYUs: # 大葉大學
                DYU(ISBN)                                             
            elif str_input[i] in CTUs: # 建國科技大學
                CTU(ISBN)  
            elif str_input[i] in NKUTs: # 南開科技大學
                NKUT(ISBN)  
            elif str_input[i] in NUKs: # 國立高雄大學
                NUK(ISBN)                                             
            elif str_input[i] in NDHUs: # 國立東華大學
                NDHU(ISBN)                 

            elif str_input[i] in TNUAs: # 國立臺北藝術大學
                TNUA(ISBN)  
            elif str_input[i] in NCUTs: # 國立勤益科技大學
                NCUT(ISBN)  
            elif str_input[i] in ISUs: # 義守大學
                ISU(ISBN)  
            elif str_input[i] in CSMUs: # 中山醫學大學
                CSMU(ISBN)  
            elif str_input[i] in NHRIs: # 國家衛生研究院
                NHRI(ISBN) 

            elif str_input[i] in NTPUs: # 國立臺北大學
                NTPU(ISBN)  
            elif str_input[i] in TPCUs: # 臺北城市科技大學
                TPCU(ISBN)  
            elif str_input[i] in TMUSTs: # 德明財經科技大學
                TMUST(ISBN)  
            elif str_input[i] in LHUs: # 龍華科技大學
                LHU(ISBN)                                                                                                                                   
            elif str_input[i] in TCPLs: # 臺中市立圖書館
                TCPL(ISBN)                  
            elif str_input[i] in CMUs: # 中國醫藥大學
                CMU(ISBN)
            elif str_input[i] in Asias: # 亞洲大學
                Asia(ISBN)
            elif str_input[i] in TNPLs: # 臺南市立圖書館
                TNPL(ISBN)
            elif str_input[i] in TCUs: # 慈濟大學
                TCU(ISBN)
            elif str_input[i] in NPUs: # 國立澎湖科技大學
                NPU(ISBN)                                                                  

            elif str_input[i] in KLCCABs: # 基隆市公共圖書館
                KLCCAB(ISBN)
            elif str_input[i] in NCLs: # 國家圖書館
                NCL(ISBN)
            elif str_input[i] in NUTCs: # 國立臺中科技大學
                NUTC(ISBN)                
            elif str_input[i] in SHUs: # 世新大學
                SHU(ISBN) 
            elif str_input[i] in TUMTs: # 台北海洋科技大學
                TUMT(ISBN)  
            elif str_input[i] in MITUSTs: # 敏實科技大學
                MITUST(ISBN)                                
            elif str_input[i] in NTUs: # 國立臺灣大學
                NTU(ISBN)
            elif str_input[i] in NCCUs: # 國立政治大學
                NCCU(ISBN)
            elif str_input[i] in TKUs: # 淡江大學
                TKU(ISBN)
            elif str_input[i] in MCUs: # 銘傳大學
                MCU(ISBN)
            elif str_input[i] in SCUs: # 東吳大學
                SCU(ISBN)      
            elif str_input[i] in NKUSTs: # 國立高雄科技大學
                NKUST(ISBN)                                                               
            elif str_input[i] in NPUSTs: # 國立屏東科技大學
                NPUST(ISBN)
            elif str_input[i] in NKUHTs: # 國立高雄餐旅大學
                NKUHT(ISBN)                
            elif str_input[i] in CGUs: # 長庚大學
                CGU(ISBN)
            elif str_input[i] in CCUs: # 國立中正大學
                CCU(ISBN)   
            elif str_input[i] in CJCUs: # 長榮大學
                CJCU(ISBN)                                 
            elif str_input[i] in MMCs: # 馬偕醫學院
                MMC(ISBN)
            elif str_input[i] in ITRIs: # 工業技術研究院
                ITRI(ISBN)
            elif str_input[i] in MCUTs: # 明志科技大學
                MCUT(ISBN)
            elif str_input[i] in CGUSTs: # 長庚科技大學
                CGUST(ISBN)
            elif str_input[i] in NTHUs: # 國立清華大學
                NTHU(ISBN)
            elif str_input[i] in NCNUs: # 國立暨南國際大學
                NCNU(ISBN)
            elif str_input[i] in NUTNs: # 國立臺南大學
                NUTN(ISBN)
            elif str_input[i] in NTCHs: # 國家兩廳院
                NTCH(ISBN)
            elif str_input[i] in NMPs: # 國立臺灣史前文化博物館
                NMP(ISBN)
            elif str_input[i] in TGSTs: # 台灣神學研究學院
                TGST(ISBN)
            elif str_input[i] in NTMOFAs: # 國立臺灣美術館
                NTMOFA(ISBN)
            elif str_input[i] in KYUs: # 高苑科技大學
                KYU(ISBN)
            elif str_input[i] in CTUSTs: # 中臺科技大學
                CTUST(ISBN)    
            elif str_input[i] in CCUSTs: # 中州科技大學
                CCUST(ISBN)                                                                                                                    
            else:
                print("nono")  

if __name__ == "__main__":
    app.run(debug=True)