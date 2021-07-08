from linebot.models import FlexSendMessage
def main_panel_flex():
    flex_message = FlexSendMessage(
                    alt_text='選擇縣市',
                    contents= {
                                "type": "bubble",
                                "hero": {
                                  "type": "image",
                                  "url": "https://github.com/yumei86/iRamen_linebot/blob/master/image/TWmap.png?raw=true",
                                  "size": "full",
                                  "aspectRatio": "20:13",
                                  "aspectMode": "cover",
                                  "position": "relative"
                                },