'''
Created on Jul 15, 2019

@author: gjwang
'''
import json
import hmac
from hashlib import sha256
from time import time

import requests
import uuid

ORDER_STATE_PENDING_SUBMIT_STR   = 'pending_submit'
ORDER_STATE_SUBMITTED_STR        = 'submitted'
ORDER_STATE_PARTIAL_FILLED_STR   = 'partial_filled'
ORDER_STATE_PARTIAL_CANCELED_STR = 'partial_canceled'
ORDER_STATE_FILLED_STR           = 'filled'
ORDER_STATE_CANCELED_STR         = 'canceled'
ORDER_STATE_PENDING_CANCEL_STR   = 'pending_cancel'
ORDER_STATE_SYS_CANCELED_STR     = 'sys_canceled'

ORDER_STATE_OPEN = (ORDER_STATE_PENDING_SUBMIT_STR, ORDER_STATE_SUBMITTED_STR, ORDER_STATE_PARTIAL_FILLED_STR,
                    ORDER_STATE_PENDING_CANCEL_STR)
ORDER_STATE_CLOSED = (ORDER_STATE_PARTIAL_CANCELED_STR, ORDER_STATE_FILLED_STR,
                      ORDER_STATE_CANCELED_STR, ORDER_STATE_SYS_CANCELED_STR,
                      )


STATUS_SUCCESS = 0


API_KEY_PRIVATE_PATH = '/api/v1/private'
API_KEY_PUBLIC_PATH = '/api/v1/public'


def get_cur_time_ms():
    """
    :return: current timestamp in milliseconds
    """
    return int(time()*1000)


class BetaExClientBase(object):
    def __init__(self, api_base_url):
        self.base_url = api_base_url
        self.private_url_base = self.base_url + API_KEY_PRIVATE_PATH
        self.public_url_base = self.base_url + API_KEY_PUBLIC_PATH

    def signature(self, api_secret, data):
        return hmac.new(api_secret, data, sha256).hexdigest()

    def get_data_str(self, data={}):
        '''
        Add nonce to data dict
        '''
        data['nonce'] = get_cur_time_ms()
        data_str = json.dumps(data, separators=(',', ':'))
        return data_str

    def get_signed_headers(self, data):
        signature = self.signature(self.api_secret.encode('utf8'), data.encode('utf8'))
        headers = {'api_key': self.api_key,
                   'signature': signature,
                   }
        return headers

    def send_request(self, url, json=None, data=None, method='POST', headers=None):
        if method=='POST':
            ret = requests.post(url, json=json, data=data, headers=headers)
        else:
            ret = requests.get(url, params=data, headers=headers)
        return ret

    def signature_test(self):
        url = self.private_url_base + '/test'

        data_str = self.get_data_str()
        signed_headers = self.get_signed_headers(data_str)
        ret = self.send_request(url, data=data_str, headers=signed_headers)
        if ret.status_code == 200:
            return json.loads(ret.text)
        else:
            err_msg = 'Something unexpected happened! http status_code=%s' %( ret.status_code)
            print(err_msg)
            raise Exception(err_msg)


class BetaExApiKeyClient(BetaExClientBase):
    """
    Use api_key/api_secret as auth
    """
    def __init__(self, url_base, api_key=None, api_secret=None):
        super(BetaExApiKeyClient, self).__init__(url_base)
        self.api_key = api_key
        self.api_secret = api_secret
    
    def get_timestamp_ms(self):
        url = self.public_url_base + '/timestamp'
        result = self.send_request(url)
        return result

    def get_symbols(self, method='GET'):
        url = self.public_url_base + '/symbols'
        result = self.send_request(url, method=method)
        return result

    def get_balance(self, account_type='trading'):
        data = {
                'currency':"BTC",
                'account_type': account_type, #default account_type=trading
                }
        
        data_str = self.get_data_str(data)
        signed_headers = self.get_signed_headers(data_str)
        url = self.private_url_base + '/balance'
        ret = self.send_request(url, None, data_str, 'POST', signed_headers)
        return ret
    
    def list_balance(self, account_type='trading'):
        data = {
                'account_type': account_type, #default account_type=trading
                }
        
        data_str = self.get_data_str(data)
        signed_headers = self.get_signed_headers(data_str)
        url = self.private_url_base + '/balance/list'
        ret = self.send_request(url, None, data_str, 'POST', signed_headers)
        return ret
    
    def create_order(self, symbol, side, qty, price, _type='limit'):
        #cid: client define order id(uuid)
        data = {'cid': 'cid_' + uuid.uuid1().hex,
                'symbol': symbol,
                'side': side,
                'qty': qty,
                'price': price,
                'type':_type,
                }

        url = self.private_url_base + '/order/create'
        data_str = self.get_data_str(data)
        signed_headers = self.get_signed_headers(data_str)
        
#         print('create_order url=%s, data_str=%s' %(url, data_str))
        ret = self.send_request(url, None, data_str, 'POST', signed_headers)
        return ret
    
    def get_order_state(self, order_id, symbol):
        data = {'order_id': order_id,
                'symbol': symbol,
                }
        
        url = self.private_url_base  + '/order/state'
        data_str = self.get_data_str(data)
        signed_headers = self.get_signed_headers(data_str)

        ret = self.send_request(url, None, data_str, 'POST', signed_headers)
        return ret
    
    def cancel_order(self, order_id, symbol):
        data = {'order_id': order_id,
                'symbol': symbol,
                }

        url = self.private_url_base + '/order/cancel'
        data_str = self.get_data_str(data)
        signed_headers = self.get_signed_headers(data_str)

        ret = self.send_request(url, None, data_str, 'POST', signed_headers)
        return ret

    def list_active_order(self, symbol):
        url = self.private_url_base + '/order/active/list'

        data = {
            'state': '',
            'side': '',
            'symbol': symbol,
            'start_tm_ms': 0,
            'end_tm_ms': get_cur_time_ms(),
            'limit': 20
        }
        if data['state']:
            assert data['state'] in ORDER_STATE_OPEN

        data_str = self.get_data_str(data);
        signed_headers = self.get_signed_headers(data_str)

        ret = self.send_request(url, None, data_str, 'POST', signed_headers)
        return ret

    def list_history_order(self, symbol):
        data = {
            'state': '',
            'side': '',
            'symbol': symbol,
            'start_tm_ms': 0,
            'end_tm_ms': get_cur_time_ms(),
            'limit': 20
        }
        if data['state']:
            assert data['state'] in ORDER_STATE_CLOSED

        data_str = self.get_data_str(data);
        signed_headers = self.get_signed_headers(data_str)

        url = self.private_url_base + '/order/history/list'
        ret = self.send_request(url, None, data_str, 'POST', signed_headers)
        return ret

    def list_trade(self, symbol):
        data = {
            'symbol': symbol,
            'start_tm_ms': 0,
            'end_tm_ms': get_cur_time_ms(),
            'limit': 20
        }
        data_str = self.get_data_str(data);
        signed_headers = self.get_signed_headers(data_str)

        url = self.private_url_base + '/trade/list'
        ret = self.send_request(url, None, data_str, 'POST', signed_headers)
        return ret
