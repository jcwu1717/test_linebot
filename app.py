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


    
def get_36h_WeatherData(locationName):
    location = locationName
    
    api_token = 'CWB-8C0CA488-FC7E-4874-9708-A91E7D54DD94'
    api_url = 'https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization='+api_token+'&locationName='+location+'&sort=time'
    try:
        r = requests.get(api_url)  # JSON data
        data_p = json.loads(r.text)  # 轉成 Python dict
        data = data_p['records']['location']  # 需求資料本體
        
        weatherData = {
            'wx' : data[0]['weatherElement'][0]
            'pop' : data[0]['weatherElement'][1]
            'min_t' : data[0]['weatherElement'][2]
            'max_t' : data[0]['weatherElement'][4]
            'cl' : data[0]['weatherElement'][3]
        }
        
        print(data_p['records']['location'][0]['locationName'] + data_p['records']['datasetDescription'] + " 已取得。")
        return weatherData
    except:
        print("try again!")

    
     
def print_36h_WeatherData(d):
    #line_bot_api.reply_message(event.reply_token, TextSendMessage(text='請問要看哪個時段的資訊？'))
    #line_bot_api.reply_message(event.reply_token, TextSendMessage(text='(1)前六小時 (2)目前時段 (3)後六小時 （請輸入數字。）'))
    
    ch = '2'
    
    if (ch == '1' or ch == '2' or ch == '3'):
        #index = int(ch)-1
        reply_str = ("天氣：" + d['wx']['time'][1]['parameter']['parameterName'] + " 機率：" + d['wx']['time'][1]['parameter']['parameterValue'] + "% \\") + \
                    ("最低溫：" + d['min_t']['time'][1]['parameter']['parameterName'] + "度 " + " 最高溫：" + d['max_t']['time'][1]['parameter']['parameterName'] + "度 \\") + \
                    ("降雨機率：" + d['pop']['time'][1]['parameter']['parameterName'] + "% \\") + \
                    ("舒適度：" + d['cl']['time'][1]['parameter']['parameterName'])
        
        return reply_str
        #line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_str))
    
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='請輸入數字。'))

# 處理文字訊息
@handler.add(MessageEvent, message=TextMessage)  # 當收到的是文字訊息時，就會啟動
def handle_message(event):
    text = event.message.text

    # 設定回覆訊息
    default_message = TextSendMessage(text=text+' meow')  # 模仿傳進來的字串，後面加喵
    
    GreetingSticker_msg = StickerSendMessage(package_id='11538',sticker_id='51626494') #打招呼貼圖
    GreetingTxext = ['hi','HI','Hi','hello','HELLO','Hello']

    # 傳訊息
    if (text in GreetingTxext):
        line_bot_api.reply_message(event.reply_token, GreetingSticker_msg) # 收到打招呼的訊息，就回復打招呼的貼圖

    elif (text == '查天氣'):
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='請問要查台灣哪裡的天氣？'))
        
    elif text == '高雄天氣':   
        ### TODO: get reply_token to trace event
        location = '高雄市'
        weatherData = get_36h_WeatherData(location)
        reply_msg = print_36h_WeatherData(weatherData) #insert event
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_msg))

    else:
        line_bot_api.reply_message(event.reply_token, default_message)  # 只有當有訊息傳來，才回覆訊息
    
        

import os, json, requests
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
