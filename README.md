# Linebot - 喵罷

## 功能

根據關鍵字回答


想把喵罷 改名 喵罷
＠喵罷 help/幫幫/問號/？: display help
=========
顯示以下文字
=========
我懂這些：
＠喵罷 start tutorial
＠喵罷 roll 2d6
＠喵罷 天氣 -欲搜尋的地名
＠喵罷 要吃什麼：隨機顯示一個有賣食物的地點

```python
bot:
    # 初始化 Flask 及 Line API
    
    # Webhook 
        設定回覆訊息
        傳訊息
        回應 HTTP 200
    # 取得氣象資料
        requests 套件
        HTTP GET
        氣象局 API 串接
        將收到的資料格式（json）轉成 Python dict
        將個項目分門別類存在字典 weatherData
        回傳資料，回應 資料已取得
    # 印出氣象資料
        印出說明文字
        請使用者輸入選項
        從 字典 印出相應資料
        使用者輸入資料錯誤偵測與攔截
    # 其他功能
        教機器人說話
        機器人講垃圾話
        提供占卜或有隨機性的功能（丟硬幣、丟骰子）
```
