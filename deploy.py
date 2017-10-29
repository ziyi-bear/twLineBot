
# coding: utf-8

# 小咖啡熊熊

from flask import Flask, request, abort

from datetime import datetime

#說明文件:https://pypi.python.org/pypi/grs
from grs import Stock #台灣上市上櫃股票價格擷取（Fetch Taiwan Stock Exchange data）含即時盤、台灣時間轉換、開休市判斷。
from grs import TWSEOpen
from grs import RealtimeWeight

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
LINE_CHANNEL_ACCESS_TOKEN = "kNHiNCQa/yIJcizd+/WR0mg7eo2LNpHRfkSxUqpbhDwrVClXFvNkLI7IAFszA/cXrXQb1pCc9/Q/nPg/kDIO7Bsu6BaJN2hI3cp0QWOItsG0ICw4uPDrVAOTJJ/csoYoJnaut+ptECCs+uwUG0vuWwdB04t89/1O/w1cDnyilFU="
LINE_CHANNEL_SECRET = "74a7e5a1026d559e92e15ea96caf811f"
NEWLINE = "\n"
STOCKRIGHT = "股票資料僅供參考，實際資料以證卷交易所網站為準，若有錯誤熊熊不附任何法律責任"

app = Flask(__name__)

#Line訊息API
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

#查詢股票資料並回傳股票資料訊息(系統提示包含)-基本計算資料顯示(五日)
def getStockInfoFromMsg(targetStockMsg):
    tempStockNumber = int(filter(str.isdigit, targetStockMsg)) #取得要查詢的目標股票號碼
    tempAskString = "系統接收到使用者請求對股票資訊的查詢 股票查詢代碼為"+str(tempStockNumber)+NEWLINE #Debug Log紀錄
    stock = Stock(str(tempStockNumber)) #擷取特定股價相關資訊
    tempMovingAverageString =  "計算五日均價與持續天數"+str(stock.moving_average(5))+NEWLINE
    tempMovingAverageValueString = "計算五日均量與持續天數"+str(stock.moving_average_value(5))+NEWLINE
    tempMovingAverageBiasRatio = "計算五日、十日乖離值與持續天數"+str(stock.moving_average_bias_ratio(5, 10))+NEWLINE
    return tempAskString+tempMovingAverageString+tempMovingAverageValueString+tempMovingAverageBiasRatio+STOCKRIGHT

#判斷台灣股市是否開市：TWSEOpen
def TWSEOpenFromMsg():
    open_or_not = TWSEOpen()
    tempIsOpen = open_or_not.d_day(datetime.today())        # 判斷今天是否開市 回傳T或F(布林)
    if tempIsOpen:
        return "今天台灣股市開市"
    else:
        return "今天台灣股市不會開市" 

#大盤即時盤資訊：RealtimeWeight（加權指數、櫃檯指數、寶島指數）故障中
def RealtimeWeightFromMsg():
    realtime_weight = RealtimeWeight() # 擷取即時大盤資訊
    #realtime_weight.raw # 原始檔案
    return str(realtime_weight.data) # 回傳 type: dict

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
    if "開市" in msg and "今天" in msg: #使用者目的是查詢今天會不會開市
        stockOpenInfo = TWSEOpenFromMsg()
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=stockOpenInfo))
    if "開市" in msg: #查詢特定日期的開市時間(省略掉了 哈)
        stockOpenInfo = TWSEOpenFromMsg()
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=stockOpenInfo))
    #if "大盤及時盤" in msg: #大盤即時盤資訊：RealtimeWeight（加權指數、櫃檯指數、寶島指數）
        #stockRealTimeWeightInfo = RealtimeWeightFromMsg()
        #line_bot_api.reply_message(event.reply_token,TextSendMessage(text=stockRealTimeWeightInfo))
    if "股票" in msg:
        stockInfoMsg = getStockInfoFromMsg(msg)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=stockInfoMsg))
    if msg=="我愛小咖啡熊熊":
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="主人我也愛你"))
    if msg=="小咖啡熊熊是正妹":
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="我是最美的小咖啡熊熊"))
    if msg=="等待建立與過濾的資料":
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="等待訓練的新模式"))
    if msg=="404實驗室":
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="有3D印表機"))
    if "誰" in msg and "我" in msg:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="我辨識您為"+str(event.message.id)))
    else:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=event.message.text))
    
@app.route('/')
def index():
    return '部屬成功'

if __name__ == "__main__":
    app.run()

