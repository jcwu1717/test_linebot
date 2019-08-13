from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)  # 宣告一個變數負責掌握 Flask server



# line_bot_api 物件初始化
# Channel Access Token
line_bot_api = LineBotApi('/4H1wt0E95nEWM3TGxgVPT7RkJ49/so8+uCV7v/eIqpudbbbkiCdrpLghCwZU63ud4bcd4rLF6UX/RYhXWKRxmtpSynYQDkc2dHb2P1CxcuZeWPO8kLVoSLZmmEZDjxU3TbnbQsSghwzsfkiffXnJgdB04t89/1O/w1cDnyilFU=')

# handler 負責處理送過來的資料
handler = WebhookHandler('19e6bc627574a011e38188c898f6cb26')  # Channel Secret

### 我還是不懂在幹嘛的東西
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
        handler.handle(body, signature) # 會自動幫你判斷要用前面設定的哪個 event
    except InvalidSignatureError:       # 檢查 Channel Access Token ，若錯誤則回傳 400 Bad Request
        abort(400)
    return 'OK'

# 處理文字訊息
@handler.add(MessageEvent, message=TextMessage)  # 當收到的是文字訊息時，就會啟動
def handle_message(event):
    # 設定回覆訊息
    message = TextSendMessage(text=event.message.text+' meow')  # 模仿傳進來的字串，後面加喵
    
    GreetingSticker_msg = StickerSendMessage(package_id='11538',sticker_id='51626494') #打招呼貼圖
    GreetingTxext = ['hi','HI','Hi','hello','HELLO','Hello']

    # 傳訊息
    if (event.message.text in GreetingTxext):
        line_bot_api.reply_message(event.reply_token, GreetingSticker_msg) # 收到打招呼的訊息，就回復打招呼的貼圖

    elif (event.message.text == '查天氣'):
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='請問要查台灣哪裡的天氣？'))
        if handle_message(event=MessageEvent, message=TextMessage):
            location = event.message.text
            m.get_36h_WeatherData(location)
            m.print_36h_WeatherData()
    else:
        line_bot_api.reply_message(event.reply_token, message)  # 只有當有訊息傳來，才回覆訊息


class bot:
    """ Meow BOT """
    def __init__(self):
        self.__name = '喵罷'
        
    def change_name(self, newName):
        self.__name = newName
        rtn_str = "我現在的名字是" + self.__name + "了！"
        return rtn_str
    
    def get_name(self):
        return self.__name
    
    def get_36h_WeatherData(self, locationName):
        self.location = locationName
        
        api_token = 'CWB-8C0CA488-FC7E-4874-9708-A91E7D54DD94'
        api_url = 'https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization='+api_token+'&locationName='+self.location+'&sort=time'
        try:
            r = requests.get(api_url)  # JSON data
            data = json.loads(r.text)  # 轉成 Python dict
            self.data = data['records']['location']  # 需求資料本體
            
            self.wx = self.data[0]['weatherElement'][0]
            self.pop = self.data[0]['weatherElement'][1]
            self.min_t = self.data[0]['weatherElement'][2]
            self.max_t = self.data[0]['weatherElement'][4]
            self.cl = self.data[0]['weatherElement'][3]
            
            print(data['records']['location'][0]['locationName'] + data['records']['datasetDescription'] + " 已取得。")
        except:
            print("try again!")

    
    @handler.add(MessageEvent, message=TextMessage)        
    def print_36h_WeatherData(self):
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='請問要看哪個時段的資訊？'))
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='(1)前六小時 (2)目前時段 (3)後六小時 （請輸入數字。）'))
        
        ch = event.message.text
        
        if (ch == '1' or ch == '2' or ch == '3'):
            index = int(ch)-1
            print("天氣：" + self.wx['time'][index]['parameter']['parameterName'], \
                    "機率：" + self.wx['time'][index]['parameter']['parameterValue'] + "%")
            print("最低溫：" + self.min_t['time'][index]['parameter']['parameterName'] + "度 "\
                    "最高溫：" + self.max_t['time'][index]['parameter']['parameterName'] + "度")
            print("降雨機率：" + self.pop['time'][index]['parameter']['parameterName'] + "%")
            print("舒適度：" + self.cl['time'][index]['parameter']['parameterName'])
        
        else:
            print("請輸入數字。")
        
        

import os, json, requests
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    m = bot()
