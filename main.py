import automate
import os
import requests

# 本番用トークンID
LINE_NOTIFY_TOKEN = os.environ['token']
# LINE Notify APIのURL
LINE_NOTIFY_API = 'https://notify-api.line.me/api/notify'
# 価格通知の敷居値
BASE_PRICE = 300000
# 商品のURL(今回は洗濯機)
CHECK_URL = 'https://www.amazon.co.jp/%E3%82%B7%E3%83%A3%E3%83%BC%E3%83%97-ES-WS13-TL-%E3%83%92%E3%83%BC%E3%83%88%E3%83%9D%E3%83%B3%E3%83%97%E4%B9%BE%E7%87%A5-DD%E3%82%A4%E3%83%B3%E3%83%90%E3%83%BC%E3%82%BF%E3%83%BC%E6%90%AD%E8%BC%89-%E5%A5%A5%E8%A1%8C727mm/dp/B08J7VWRCB/ref=sr_1_10?__mk_ja_JP=%E3%82%AB%E3%82%BF%E3%82%AB%E3%83%8A&dchild=1&keywords=%E6%B4%97%E6%BF%AF%E6%A9%9F+%E3%83%89%E3%83%A9%E3%83%A0&qid=1619215236&sr=8-10'

# 値段情報を取得して整形してレスポンスする。


def getPrice(content):
    # 値段の先頭の￥, 3桁区切りの,を''に変更する。
    return int(content.text.replace('￥', '').replace(',', ''))


# エントリーポイント
def check_price(event, context):
    # seleniumに関するinstance生成を行う。
    selenium = automate.Selenium()

    # amazonの洗濯機詳細ページに移動
    selenium.access(CHECK_URL)
    # ページ読み込みのために遅延させる。
    selenium.stop(5)

    # 洗濯機の値段要素を指定
    selenium.find_element_by_id('price_inside_buybox')
    # 値段を取得して整形してpriceへ格納する。
    price = getPrice(selenium.get_element())

    # 通知判定、敷居値より安い値段の場合に通知する。
    if price <= BASE_PRICE:
        # Notify URL
        payload = {'message': "現在の価格は" + str(price) +
                   "円です。敷居値より安くなっております。(敷居値 : " + str(BASE_PRICE) + "円)\n" + CHECK_URL}
        headers = {'Authorization': 'Bearer ' + LINE_NOTIFY_TOKEN}
        requests.post(LINE_NOTIFY_API, data=payload, headers=headers)

    # 処理終了
    selenium.quit()
