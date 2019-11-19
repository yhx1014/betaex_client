#-*- coding:utf-8 -*-

'''
Created on  Nov 19, 2019

@author: gjwang
'''

import logging
from time import time
import os

def get_cur_time_ms():
    '''
    return current timestamp in milliseconds
    '''
    return int( time()*1000 )

def log_config(log_dir='.', filename='log_test.log', is_debug=True):
    logginglevel = logging.DEBUG if is_debug else logging.INFO

    log_dir = os.path.join(log_dir, 'log')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_filename=os.path.join(log_dir, filename)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
    log_FileHandler = logging.handlers.TimedRotatingFileHandler(log_filename,
                                                                when='D',  # log file rollover every 24 hours
                                                                interval=1,
                                                                backupCount=30)

    log_FileHandler.setFormatter(formatter)
    log_FileHandler.setLevel(logginglevel)
    logger = logging.getLogger()
    logger.setLevel(logginglevel)
    logger.addHandler(log_FileHandler)



