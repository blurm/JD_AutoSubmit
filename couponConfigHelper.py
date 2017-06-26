#!/usr/bin/env python
# -*- coding: utf-8 -*-

from configparser import ConfigParser
import datetime

cfg = ConfigParser()
cfg.read('couponConfig.ini')


def readGovIDNumber(area, test):
    if test:
        return cfg.get("govidnumber", area + "_test")
    else:
        return cfg.get("govidnumber", area)


def readURL(name):
    return cfg.get("url",name)


def readMode(mode):
    return cfg.getboolean('mode', mode)

def readEngine():
    return cfg.get('engine', 'engine')

def readPhoneNumber(test):
    if test:
        return cfg.get('phoneNumber', 'phoneNumber_test')
    else:
        return cfg.get('phoneNumber', 'phoneNumber')


def readCMPhoneNumber(test):
    if test:
        return cfg.get('phoneNumber', 'CMPhoneNumber_test')
    else:
        return cfg.get('phoneNumber', 'CMPhoneNumber')


def writeRCode(rcode, accountId):
    cfg.set('rcode', 'code', rcode)
    cfg.set('rcode', 'account', accountId)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cfg.set('rcode', 'time', now)
    cfg.write(open('config.ini', 'w'))


def readRCode():
    rcode = cfg.get('rcode', 'code')
    # timeStr = cfg.get('rcode', 'time')
    # result = {
            # 'rcode': rcode,
            # 'time': timeStr
            # }
    return rcode


def readConfig(config):
    return cfg.getint('config', config)


def test():
    rcodeDict = readRCode()
    print(rcodeDict)

    # if smscode is empty, means last code is still available
    # need to retrieve it from file
    smsCode = ""
    # if len(smsCode) < 1:
        # rcodeDict = readRCode()
        # time = datetime.strftime(rcodeDict['time'], '%Y-%m-%d %H:%M:%S')
        # # if diffTimeNow(time) > 
        # smsCode = "needtofetch from file"

    # print int((datetime.datetime.now() - datetime.datetime(2016,9,28,9,9,0)).total_seconds()/60)

    print(readGovIDNumber('beijing'))

