#-*- coding:utf-8 -*-

import json
from betaex_client import BetaExApiKeyClient

API_BASE_URL = 'https://api.betaex.com'
API_KEY = 'KeyswwUPK8UqBJ3U63k6QOvAIE2GeDkBQetaiCog0hsC34iHeiQs80oYtiLEbo9R'
API_SECRET = 'SecFKhuXMEZHJYMTOVHIyiFHXhdke04K40HOAoFi7eYrMbVtLqphbfqN89HEy6d5'

betaexClient = BetaExApiKeyClient(API_BASE_URL, API_KEY, API_SECRET)
print(betaexClient.signature_test())

#list trade acccount balance
ret = betaexClient.list_balance()
result = json.loads(ret.text)
print(result)
