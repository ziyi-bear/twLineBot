
# coding: utf-8

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

LINE_CHANNEL_ACCESS_TOKEN = "mQVYL9n3SSe3W7LWU8vSEHLeu2Wr9Bk7B/e8lLTvbBIiqjCGWWc88YkCWIFrUtKH2oA+U5i8YO8FC4EEy2XAFdsXG7D6y7DVPFlk5zgEff205cB3rQ+jF2ilszTcE7wwcNEmg802/gAHBXJAlJ8WqAdB04t89/1O/w1cDnyilFU="
LINE_CHANNEL_SECRET = "2d88fd33111410911fb8fe0ce0d55e45"

app = Flask(__name__)

line_bot_api = LineBotApi('LINE_CHANNEL_ACCESS_TOKEN')
handler = WebhookHandler('LINE_CHANNEL_SECRET')


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


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

