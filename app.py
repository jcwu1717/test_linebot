from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('/4H1wt0E95nEWM3TGxgVPT7RkJ49/so8+uCV7v/eIqpudbbbkiCdrpLghCwZU63ud4bcd4rLF6UX/RYhXWKRxmtpSynYQDkc2dHb2P1CxcuZeWPO8kLVoSLZmmEZDjxU3TbnbQsSghwzsfkiffXnJgdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('19e6bc627574a011e38188c898f6cb26')

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
    return 'OK'

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = TextSendMessage(text=event.message.text+' meow')
    GreetingSticker = StickerSendMessage(
    package_id='11538',
    sticker_id='51626494'
    )
    if (event.message.text == 'hi'):
        line_bot_api.reply_message(event.reply_token, GreetingSticker)
    else:
        line_bot_api.reply_message(event.reply_token, message)  # 只有當有訊息傳來，才回覆訊息

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
