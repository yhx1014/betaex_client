import json
from time import time
import logging

from tornado.ioloop import IOLoop, PeriodicCallback
from tornado import gen
from tornado.websocket import websocket_connect
from tornado.gen import coroutine

from utils import get_cur_time_ms
from utils import log_config

from ws_client import BetaExWsClient
from ws_client import CHAN_TRADE, CHAN_TICKER, CHAN_ORDERBOOK, CHAN_KLINE

WS_BASE_URL = 'wss://ws.betaex.com/sub'


class BetaExWsClientDemo(BetaExWsClient):
    @coroutine
    def on_message(self, msg):
        print 'BetaExWsClientDemo, on_message=', msg
        msg_json = json.loads(msg)
        yield self.message_dispatch(msg)

    @coroutine
    def on_connected(self):
        print('connected success')
    
    @coroutine
    def message_dispatch(self, msg):
        pass
    

IS_DEBUG = True
if __name__ == "__main__":
    log_config()

    timeout = 5
    
    symbol = 'BTC_USDT'
    chan_id = CHAN_TRADE.format(symbol=symbol)
#     chan_id = CHAN_ORDERBOOK.format(symbol=symbol)
#     chan_id = CHAN_KLINE.format(symbol=symbol, kline_interval=KLINE_INTERVAL_1M)
#     chan_id = CHAN_TICKER.format(symbol=symbol)


    sub_url = WS_BASE_URL + '?id=' + chan_id
    client = BetaExWsClientDemo(sub_url, timeout)