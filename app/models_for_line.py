# 處理觸發事件

from app import handler, line_bot_api

from linebot.models import MessageEvent, TextMessage, TextSendMessage

"""
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token, 
        TextSendMessage(text=f"Hello {line_bot_api.get_profile(event.source.user_id).display_name}!")
    )
"""
    
# 學你說話
@handler.add(MessageEvent, message=TextMessage)
def echo(event):
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text=event.message.text)
    )