
# coding: utf-8

# 小咖啡熊熊

from flask import Flask, request, abort

#說明文件:https://pypi.python.org/pypi/grs
from grs import Stock #台灣上市上櫃股票價格擷取（Fetch Taiwan Stock Exchange data）含即時盤、台灣時間轉換、開休市判斷。

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

#Line訊息API的所需參數
LINE_CHANNEL_ACCESS_TOKEN = "mQVYL9n3SSe3W7LWU8vSEHLeu2Wr9Bk7B/e8lLTvbBIiqjCGWWc88YkCWIFrUtKH2oA+U5i8YO8FC4EEy2XAFdsXG7D6y7DVPFlk5zgEff205cB3rQ+jF2ilszTcE7wwcNEmg802/gAHBXJAlJ8WqAdB04t89/1O/w1cDnyilFU="
LINE_CHANNEL_SECRET = "2d88fd33111410911fb8fe0ce0d55e45"

app = Flask(__name__)

#Line訊息API
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

#查詢股票資料並回傳股票資料訊息(系統提示包含)
def getStockInfoFromMsg(targetStockMsg):
    tempStockNumber = int(filter(str.isdigit, targetStockMsg))      #取得要查詢的目標股票號碼
    print("系統接收到使用者請求對股票資訊的查詢 股票查詢代碼為", tempStockNumber) #Debug Log紀錄
    stock = Stock(tempStockNumber)                                  #擷取長榮航股價
    return "計算五日均價與持續天數"+stock.moving_average(5)        #計算五日均價與持續天數
    #print(stock.moving_average_value(5))                        #計算五日均量與持續天數
    #print(stock.moving_average_bias_ratio(5, 10))               #計算五日、十日乖離值與持續天數

#被Line Message API呼叫運作
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value 回覆所需的簽章(會不斷變換)
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body 處理webhook事件
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    print("使用者傳送的訊息為", msg)
    msg = msg.encode('utf-8')
    if "股票" in msg:
        stockInfoMsg = getStockInfoFromMsg(msg)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=stockInfoMsg))
    if msg=="我愛小咖啡熊熊":
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="主人我也愛你"))
    if msg=="小咖啡熊熊是正妹":
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="我是最美的小咖啡熊熊"))
    if msg=="等待建立與過濾的資料":
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="等待訓練的新模式"))
    else:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=event.message.text))
    
@app.route('/')
def index():
    return '部屬成功'


if __name__ == "__main__":
    app.run()

