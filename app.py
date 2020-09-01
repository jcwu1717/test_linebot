# ================= 機器人初始化 開始 =================
import os, json, requests, random
import urllib.request as urlrequest
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
# ================= 機器人初始化 結束 =================


# ================= 自訂功能區 開始 ================
# 機器人使用說明
def bot_help():
    helpText = "歡迎使用喵罷，以下是我會做的事，輸入冒號後的指令以使用該功能\n------------------------------\n" + \
                "丟硬幣：丟硬幣\n" + \
                "查詢高雄天氣：高雄天氣\n" + \
                "查詢台北天氣：台北天氣\n" + \
                "使用高雄天氣小幫手：高雄天氣小幫手\n" + \
                "使用台北天氣小幫手：台北天氣小幫手\n" + \
                "查詢最近的地震：地震\n" + \
                "查詢高雄美食：吃"
    return helpText

# 丟硬幣
def roll_coin():
    result = random.randint(0,1)
    if result == 0:
        return '反面'
    else:
        return '正面'
# 使用氣象局 API 抓取鄉鎮36小時天氣資訊    
def get_36h_WeatherData(locationName):
    location = locationName
    
    api_token = 'CWB-8C0CA488-FC7E-4874-9708-A91E7D54DD94'
    api_url = 'https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization='+api_token+'&locationName='+location+'&sort=time'
    try:
        r = requests.get(api_url)  # JSON data
        data_p = json.loads(r.text)  # 轉成 Python dict
        data = data_p['records']['location']  # 需求資料本體
        
        weatherData = {
            'wx': data[0]['weatherElement'][0], \
            'pop': data[0]['weatherElement'][1], \
            'min_t': data[0]['weatherElement'][2], \
            'max_t': data[0]['weatherElement'][4], \
            'cl': data[0]['weatherElement'][3]
        }
        
        print(data_p['records']['location'][0]['locationName'] + data_p['records']['datasetDescription'] + " 已取得。")
        return weatherData
    except:
        print("try again!")

def weather_helper(locationName):
    location = locationName
    api_token = 'CWB-8C0CA488-FC7E-4874-9708-A91E7D54DD94'
    name = ['台北市','新北市','基隆市','花蓮縣','宜蘭縣','金門縣','澎湖縣','台南市','高雄市','嘉義縣','嘉義市','苗栗縣','台中市','桃園市','新竹縣','新竹市','屏東縣','南投縣','台東縣','彰化縣','雲林縣','連江縣']
    if location == '台北市':
        data_id = '09'
    else:
        data_id = name.index(location)+9
    fileAPI_url = 'https://opendata.cwb.gov.tw/fileapi/v1/opendataapi/F-C0032-0'+str(data_id)+'?Authorization='+api_token+'&format=JSON'
    
    r = requests.get(fileAPI_url)
    etag = r.headers['ETag']
    headers = {'If-None-Match': etag}

    # 檢查資料是否有更新（Etag 使用者快取機制）
    try:
        if requests.get(fileAPI_url,headers=headers).status_code == 304:
            print("資料未更新")

        if requests.get(fileAPI_url,headers=headers).status_code == 200:
            print("資料已更新")
            etag = requests.get(fileAPI_url,headers=headers).headers['ETag']
            r = requests.get(fileAPI_url,headers=headers)
    except:
        print("伺服器發生錯誤 Try again!")  

    # 天氣訊息處理
    try:    
        data_p = json.loads(r.text)  # 轉成 Python dict    
        weatherData = '🌦來自天氣小幫手的提醒：\n\n'
        for v in data_p['cwbopendata']['dataset']['parameterSet']['parameter']:
            weatherData += '➢ ' + v['parameterValue'] + '\n'
        weatherData += '➡️ 更多天氣訊息：https://www.cwb.gov.tw/V8/C/'
                    
        # 於終端機顯示已取得資料的訊息    
        print(data_p['cwbopendata']['dataset']['datasetInfo']['issueTime'] + ' ' +data_p['cwbopendata']['dataset']['location']['locationName'] + data_p['cwbopendata']['dataset']['datasetInfo']['datasetDescription'] + " 已取得。")
        return weatherData
    except:
        print("資料處理發生錯誤 Try again!")


def get_earthquakeData():
    api_url = 'https://opendata.cwb.gov.tw/api/v1/rest/datastore/E-A0015-001?Authorization=CWB-8C0CA488-FC7E-4874-9708-A91E7D54DD94&limit=3'
    try:
        r = requests.get(api_url)  # JSON data
        rawData = json.loads(r.text)  # 轉成 Python dict
        reportContent = rawData['records']['earthquake'][0]['reportContent']
        img_url = rawData['records']['earthquake'][0]['reportImageURI']
        return reportContent, img_url
    except:
        print("try again!")

# 使用高雄城市資料平台提供之 API
def get_kh_food():
    src = "https://api.kcg.gov.tw:443/api/service/Get/d42e9a5a-d176-47fe-9ff9-7a49d4fe01bd"
    
    with urlrequest.urlopen(src) as response:
        data = json.load(response)

    shoplist = data['data']
    shop = shoplist[random.randint(1,len(data['data']))] # 隨機抽取一家店
    reply_str = shop['name'] + "\n" + \
                shop['description'] + "\n" + \
                "營業時間：", shop['opentime'] + "\n" + \
                "地址：", shop['add'] + "\n" + \
                "電話：", shop['tel'] + "\n" + \
                "Website：", shop['website'] + "\n" + \
                "資料更新時間：", shop['updatetime'] + "\n" + \
                "資料來源：高雄城市資料平台-高雄旅遊網-餐飲資料"
    reply_str = "".join(reply_str)
    return reply_str
    

# ================= 自訂功能區 結束 ================

    
# ================= 測試區 開始 ================     

# ================= 測試區 結束 ==============


# ================= 機器人傳訊區塊 開始 =================
# 處理文字訊息
@handler.add(MessageEvent, message=TextMessage)  # 當收到的是文字訊息時，就會啟動
def handle_message(event):
    text = event.message.text

    # 設定預設回覆訊息
    default_message = TextSendMessage(text=text+' 喵')  # 模仿傳進來的字串，後面加喵
    # 設定預設打招呼訊息
    GreetingSticker_msg = StickerSendMessage(package_id='11538',sticker_id='51626494') #打招呼貼圖
    GreetingTxext = ['hi','HI','Hi','hello','HELLO','Hello','嗨','你好','哈囉','您好','尼好'] # 能被接受的打招呼字串

    # 傳訊息
    if text in GreetingTxext:
        line_bot_api.reply_message(event.reply_token, GreetingSticker_msg) # 收到打招呼的訊息，就回復打招呼的貼圖
    
    elif text == 'profile':
        if isinstance(event.source, SourceUser):
            profile = line_bot_api.get_profile(event.source.user_id)
            line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(text='Display name: ' + profile.display_name),
                    TextSendMessage(text='Status message: ' + str(profile.status_message))
                ]
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="Bot can't use profile API without user ID"))
    # NEED Update
    elif (text == '查天氣'):
        ### TODO: 使用使用者位置查詢天氣 get reply_token to trace event
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='請問要查台灣哪裡的天氣？'))
        
    elif text == '高雄天氣':   
        location = '高雄市'
        weatherData = get_36h_WeatherData(location)
        reply_msg = '🌏天氣：' + weatherData['wx']['time'][1]['parameter']['parameterName'] + '(' + weatherData['wx']['time'][1]['parameter']['parameterValue'] + '%)\n' + \
                    '🔹最低溫：' + weatherData['min_t']['time'][1]['parameter']['parameterName'] + '度，' + '🔸最高溫：' + weatherData['max_t']['time'][1]['parameter']['parameterName'] + '度\n' + \
                    '🌧降雨機率：' + weatherData['pop']['time'][1]['parameter']['parameterName'] + '%\n' + \
                    '👣舒適度：' + weatherData['cl']['time'][1]['parameter']['parameterName']
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=reply_msg))
    elif text == '台北天氣' or text == '臺北天氣':   
        location = '臺北市'
        weatherData = get_36h_WeatherData(location)
        reply_msg = '天氣：' + weatherData['wx']['time'][1]['parameter']['parameterName'] + '(' + weatherData['wx']['time'][1]['parameter']['parameterValue'] + '%)\n' + \
                    '🔹最低溫：' + weatherData['min_t']['time'][1]['parameter']['parameterName'] + '度，' + '🔸最高溫：' + weatherData['max_t']['time'][1]['parameter']['parameterName'] + '度\n' + \
                    '🌧降雨機率：' + weatherData['pop']['time'][1]['parameter']['parameterName'] + '%\n' + \
                    '👣舒適度：' + weatherData['cl']['time'][1]['parameter']['parameterName']
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=reply_msg))

    elif text == '高雄天氣小幫手':
        location = '高雄市'
        weather_msg = weather_helper(location)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=weather_msg))
    
    elif text == '台中天氣小幫手':
        location = '台中市'
        weather_msg = weather_helper(location)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=weather_msg))

    elif text == '台北天氣小幫手':
        location = '台北市'
        weather_msg = weather_helper(location)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=weather_msg))

    elif text == '新北天氣小幫手':
        location = '新北市'
        weather_msg = weather_helper(location)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=weather_msg))

    elif text == '基隆天氣小幫手':
        location = '基隆市'
        weather_msg = weather_helper(location)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=weather_msg))

    elif text == '花蓮天氣小幫手':
        location = '花蓮縣'
        weather_msg = weather_helper(location)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=weather_msg))

    elif text == '宜蘭天氣小幫手':
        location = '宜蘭縣'
        weather_msg = weather_helper(location)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=weather_msg))

    elif text == '金門天氣小幫手':
        location = '金門縣'
        weather_msg = weather_helper(location)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=weather_msg))
    
    elif text == '澎湖天氣小幫手':
        location = '澎湖縣'
        weather_msg = weather_helper(location)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=weather_msg))

    elif text == '台南天氣小幫手':
        location = '台南市'
        weather_msg = weather_helper(location)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=weather_msg))

    elif text == '嘉義縣天氣小幫手':
        location = '嘉義縣'
        weather_msg = weather_helper(location)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=weather_msg))
    
    elif text == '嘉義市天氣小幫手':
        location = '嘉義市'
        weather_msg = weather_helper(location)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=weather_msg))
    
    elif text == '苗栗天氣小幫手':
        location = '苗栗縣'
        weather_msg = weather_helper(location)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=weather_msg))
    
    elif text == '桃園天氣小幫手':
        location = '桃園縣'
        weather_msg = weather_helper(location)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=weather_msg))

    elif text == '新竹縣天氣小幫手':
        location = '新竹縣'
        weather_msg = weather_helper(location)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=weather_msg))
    
    elif text == '新竹市天氣小幫手':
        location = '新竹市'
        weather_msg = weather_helper(location)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=weather_msg))
    
    elif text == '南投天氣小幫手':
        location = '南投縣'
        weather_msg = weather_helper(location)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=weather_msg))

    elif text == '屏東天氣小幫手':
        location = '屏東縣'
        weather_msg = weather_helper(location)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=weather_msg))

    elif text == '台東天氣小幫手':
        location = '台東縣'
        weather_msg = weather_helper(location)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=weather_msg))
    
    elif text == '彰化天氣小幫手':
        location = '彰化縣'
        weather_msg = weather_helper(location)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=weather_msg))
    
    elif text == '雲林天氣小幫手':
        location = '雲林縣'
        weather_msg = weather_helper(location)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=weather_msg))
    
    elif text == '連江縣天氣小幫手':
        location = '連江縣'
        weather_msg = weather_helper(location)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=weather_msg))
    
    

    # 回傳高雄市旅遊網推薦的其中一個美食
    elif text == '吃':
        eatdata = get_kh_food()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=eatdata))

    # 回傳最近的顯著有感地震報告
    elif text == '地震':
        report, reportImgURL = get_earthquakeData()

        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(text=report),
                ImageSendMessage(
                    original_content_url=reportImgURL,
                    preview_image_url=reportImgURL
                )
            ]
        )
    elif text == '丟硬幣':
        #coin = roll_coin()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='你丟到'+roll_coin()+'！'))
    elif text == 'help':
        reply_message = bot_help()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))
        

    else:
        print('Receive:',text) # For debug
        line_bot_api.reply_message(event.reply_token, default_message)  # 只有當有訊息傳來，才回覆預設訊息
# ================= 機器人傳訊區塊 結束 =================
        
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
