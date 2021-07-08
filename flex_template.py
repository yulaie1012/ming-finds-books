from linebot.models import FlexSendMessage
def main_panel_flex():
    flex_message = FlexSendMessage(
                    alt_text='選擇縣市',
                    contents= {
                                "type": "bubble",
                                "hero": {
                                  "type": "image",
                                  "url": "https://github.com/yulaie1012/MingFindsBooks/blob/master/image/location.png?raw=true",
                                  "size": "full",
                                  "aspectRatio": "20:13",
                                  "aspectMode": "cover",
                                  "position": "relative"
                                },
                                "body": {
                                  "type": "box",
                                  "layout": "vertical",
                                  "contents": [
                                    {
                                      "type": "text",
                                      "text": "想找哪裡的圖書館呢？",
                                      "weight": "bold",
                                      "size": "xl",
                                      "contents": [],
                                      "color": "#6e3e1e"
                                    },
                                    {
                                      "type": "text",
                                      "text": "請幫助我選擇圖書館在台灣的哪個位置：）",
                                      "size": "xs",
                                      "margin": "sm"
                                    },
                                    {
                                      "type": "separator",
                                      "margin": "lg"
                                    },
                                    {
                                      "type": "box",
                                      "layout": "horizontal",
                                      "contents": [
                                        {
                                          "type": "button",
                                          "action": {
                                            "type": "message",
                                            "label": "北部",
                                            "text": "北部"
                                          },
                                          "style": "primary",
                                          "height": "sm",
                                          "color": "#806408"
                                        },
                                        {
                                          "type": "button",
                                          "action": {
                                            "type": "message",
                                            "label": "中部",
                                            "text": "中部"
                                          },
                                          "style": "primary",
                                          "margin": "xxl",
                                          "height": "sm",
                                          "color": "#806408"
                                        }
                                      ],
                                      "margin": "lg"
                                    },
                                    {
                                      "type": "box",
                                      "layout": "horizontal",
                                      "contents": [
                                        {
                                          "type": "button",
                                          "action": {
                                            "type": "message",
                                            "label": "南部",
                                            "text": "南部"
                                          },
                                          "style": "primary",
                                          "height": "sm",
                                          "color": "#806408"
                                        },
                                        {
                                          "type": "button",
                                          "action": {
                                            "type": "message",
                                            "label": "東部",
                                            "text": "東部"
                                          },
                                          "style": "primary",
                                          "margin": "xxl",
                                          "height": "sm",
                                          "color": "#806408"
                                        }
                                      ],
                                      "margin": "md"
                                    }
                                    ]                     
                                }
                    }
    )
    return flex_message