#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on Nov 19, 2019

@author: gjwang
'''

import json
from time import time
import logging

from tornado.ioloop import IOLoop, PeriodicCallback
from tornado import gen
from tornado.websocket import websocket_connect
from tornado.gen import coroutine

from utils import get_cur_time_ms
from utils import log_config


WS_BASE_URL = 'wss://ws.betaex.com/sub'


CHAN_ORDERBOOK = 'orderbook.{symbol}.L20'
CHAN_TRADE = 'trade.{symbol}'
CHAN_TICKER = 'ticker.{symbol}'
CHAN_KLINE = 'kline.{symbol}.{kline_interval}'

KLINE_INTERVAL_1M = '1m'


PING_INTERVAL_MS = 30*1000
MAX_NO_MSG_INTERVAL_SECS = 30
CHECK_INTEVAL_MS = 10*1000

PING_MSG = 'PING'
PONG_RES = 'POND'


class BetaExWsClient(object):
    def __init__(self, url, timeout, **kwargs):
        super(BetaExWsClient, self).__init__()

        self.url = url
        self.timeout = timeout
        self.ws = None
        self.last_recv_time_ms = 0  # use to determine is ws is still alive or not
        self.max_no_msg_interval_ms = MAX_NO_MSG_INTERVAL_SECS*1000  # consider ws is dead
        self.ping_msg = PING_MSG

        self.initialize(**kwargs)

        self.connect()

#         PeriodicCallback(self.keep_alive, PING_INTERVAL_MS).start()
        PeriodicCallback(self.is_ws_dead, CHECK_INTEVAL_MS).start()

        self.ioloop = IOLoop.instance()
        self.ioloop.start()

    def initialize(self, **kwargs):
        """Hook for subclass initialization. Called for on object init
        """
        pass

    @gen.coroutine
    def connect(self):
        logging.info("connecting...")
        print("ws_url=%s" % self.url)
        try:
            self.last_recv_time_ms = get_cur_time_ms()
            self.ws = yield websocket_connect(self.url)
        except Exception as e:
            logging.error("connection error=%s", str(e))
        else:
            logging.info("connected")
            self.on_connected()
            self.run()

    @gen.coroutine
    def run(self):
        while True:
            msg = yield self.ws.read_message()
            if msg is None:
                logging.error("connection closed")
                self.ws = None
                break

            self.last_recv_time_ms = get_cur_time_ms()

            try:
                self.on_message(msg)
            except Exception as ex:
                logging.error("on_message exception=%s", str(ex))

    @coroutine
    def on_connected(self):
        print('on_connected')

    @coroutine
    def on_message(self, msg):
        print('on_message, ', msg)

    def is_ws_dead(self):
        '''
        A ws watchdog
        '''
        now = get_cur_time_ms()
        is_dead = (now - self.last_recv_time_ms) > self.max_no_msg_interval_ms
        if is_dead:
            logging.error("ws is dead")
            self.ws = None  # close the old ws
            self.reconnect()

        return is_dead

    def reconnect(self):
        logging.error("reconnecting...")
        self.ws = None
        self.connect()

    def keep_alive(self):
        if self.ws is None:
            self.reconnect()
        else:
            self.ws.write_message(self.ping_msg)
