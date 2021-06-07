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


# 學你說話
@handler.add(MessageEvent, message=TextMessage)
def echo(event):
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text=event.message.text)
    )
"""       
# Phoebe愛唱歌
@handler.add(MessageEvent, message=TextMessage)
def pretty_echo(event):
    
    if event.source.user_id != "Udeadbeefdeadbeefdeadbeefdeadbeef":
        
        pretty_note = '♫♪♬'
        pretty_text = ''
        
        for i in event.message.text:
        
            pretty_text += i
            pretty_text += random.choice(pretty_note)
    
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=pretty_text)
        )