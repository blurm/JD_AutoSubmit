import requests
import random
import json
import os
import time
import multiprocessing

import re
from lxml import etree
from rk import *
from pyquery import PyQuery as pq
from configparser import ConfigParser
import datetime
import sched
from bcolors import bcolors

url = 'https://passport.jd.com/new/login.aspx'

headers = {
    'User-Agent':
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36',
    'ContentType':
    'text/html; charset=utf-8',
    'Accept-Encoding':
    'gzip, deflate, sdch',
    'Accept-Language':
    'zh-CN,zh;q=0.8',
    'Connection':
    'keep-alive',
}

s = requests.Session()
s.headers = headers

cfg = ConfigParser()
cfg.read('couponConfig.ini')

# 请求登录页面
req1 = s.get(url=url, headers=headers)

sel = etree.HTML(req1.content)
uuid = sel.xpath('//input[@id="uuid"]/@value')[0]

eid = sel.xpath('//input[@id="eid"]/@value')[0]
sa_token = sel.xpath('//input[@id="sa_token"]/@value')[0]
pubKey = sel.xpath('//input[@id="pubKey"]/@value')[0]
t = sel.xpath('//input[@id="token"]/@value')[0]

r = random.random()
login_url = 'https://passport.jd.com/uc/loginService'


class JD(object):
    def __init__(self, username, password, rk_username=None, rk_pwd=None):
        self.username = username
        self.password = password
        rk_username = "wallflower"
        rk_pwd = "mjq123456"
        self.rkclient = RClient(rk_username, rk_pwd)
        self.trackid = ''
        self.pid = ''
        self.cookies = {}

    # 账号登录函数
    def login(self):

        params = {
            'uuid': uuid,
            'eid': eid,
            # 'fp': 'a2fd52211772d8fea0515bedca560b0b',
            '_t': t,
            'loginType': 'c',
            'loginname': self.username,
            'nloginpwd': self.password,
            'chkRememberMe': '',
            'authcode': '',
            'pubKey': pubKey,
            'sa_token': sa_token,
            # 'seqSid': '5574250748814772000'
        }

        headers = {
            'Referer':
            'https://passport.jd.com/uc/login?ltype=logout',
            'User-Agent':
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36',
            'X-Requested-With':
            'XMLHttpRequest'
        }

        # logout first
        s.get("https://passport.jd.com/uc/login?ltype=logout")

        # 验证码图片
        imgcode = 'http:' + sel.xpath('//img[@id="JD_Verification1"]/@src2')[0]
        img = requests.get(imgcode)
        # 把这个路径替换成自己电脑jd.py文件夹的路径，/Users/zhangkai/Desktop/JD
        with open('/home/damon/mydata/git/JD_Utils/authcode.jpg', 'wb') as f:
            f.write(img.content)
        im = open('authcode.jpg', 'rb').read()
        print('开始识别验证码...')

        # print(imgcode)   # 手动验证码连接
        imgcode1 = input("请输入验证码:")

        # 自动打码
        # imgcode1 = self.rkclient.rk_create(im, 3040)['Result']
        print(bcolors.OKGREEN + imgcode1)

        if imgcode != '':

            # params['authcode'] = input('请输入验证码：')  # 手动输验证码

            params['authcode'] = str(imgcode1)
            req2 = s.post(login_url, data=params, headers=headers)

            patt = '<Cookie TrackID=(.*?) for .jd.com/>'
            self.trackid = re.compile(patt).findall(str(s.cookies))

            js = json.loads(req2.text[1:-1])
            print(js)
            if js.get('success'):
                print('登录成功')
            else:
                print('登录失败')
                raise Exception("Login failed")
        else:
            req2 = s.post(login_url, data=params, headers=headers)

            patt = '<Cookie TrackID=(.*?) for .jd.com/>'
            self.trackid = re.compile(patt).findall(str(s.cookies))

            js = json.loads(req2.text[1:-1])

            if js.get('success'):
                print('登录成功')
            else:
                print('登录失败')
                raise Exception("Login failed")

    def addcart(self):

        self.pid = input('请输入要加入购物车的商品编号：')
        pcount = input('请输入加入数量：')
        add_carturl = 'https://cart.jd.com/gate.action?pid=' + self.pid + '&pcount=' + pcount + '&ptype=1'
        # add_carturl = 'https://cart.jd.com/gate.action?pid=3659204&pcount=1&ptype=1'

        req4 = s.get(add_carturl)

        if re.compile('<title>(.*?)</title>').findall(
                req4.text)[0] == '商品已成功加入购物车':
            print('商品已成功加入购物车')
        else:
            print('添加购物车失败')

    def submit(self):
        # 购物车页面
        carturl = 'https://cart.jd.com'
        req5 = s.get(carturl)

        # 取消选择某个商品
        cancelitemurl = 'https://cart.jd.com/cancelItem.action?rd' + str(r)
        form_data = {
            'outSkus': '',
            'pid': self.pid,  # 商品id
            'ptype': '1',
            'packId': '0',
            'targetId': '0',
            'promoID': '0',
            'locationId': '1-2810-6501-0'  # 地址代码
        }

        req6 = s.post(cancelitemurl, data=form_data)

        # 选择某个商品
        selectitemurl = 'https://cart.jd.com/selectItem.action?rd' + str(r)
        req7 = s.post(selectitemurl, data=form_data)

        timestamp = int(time.time() * 1000)
        # 订单结算页
        orderInfo = 'https://trade.jd.com/shopping/order/getOrderInfo.action?rid=' + str(
            timestamp)

        # 提交订单url
        submitOrder = 'https://trade.jd.com/shopping/order/submitOrder.action'

        submit_data = {
            'overseaPurchaseCookies': '',
            'submitOrderParam.sopNotPutInvoice': 'false',
            'submitOrderParam.trackID': self.trackid[0],
            'submitOrderParam.ignorePriceChange': '0',
            'submitOrderParam.btSupport': '0',
            'submitOrderParam.eid': eid,
            'submitOrderParam.fp': 'b31fc738113fbc4ea5fed9fc9811acc6',
            # 'riskControl': 'D0E404CB705B9732D8D7A53159E363F2140ADCDE164C1F9CABA71F1D7552B70E5C9C6041832CEB4B',
        }

        ordertime = input('''请选择：
                          1.设置下单时间
                          2.选择立即下单(可用于监控库存，自动下单)
                          请输入选择（1/2):
                          ''')

        if ordertime == '1':
            set_time = input('请按照2017-05-01 23:11:11格式输入下单时间:')
            timeArray = time.mktime(
                time.strptime(set_time, '%Y-%m-%d %H:%M:%S'))
            while True:
                if time.time() >= timeArray:

                    print('正在提交订单...')
                    req8 = s.post(submitOrder, data=submit_data)
                    js1 = json.loads(req8.text)
                    print(js1)
                    # 判断是否下单成功
                    if js1['success'] == True:
                        print('下单成功!')
                    else:
                        print('下单失败')
                    break
                else:
                    # print('等待下单...')
                    continue
        # 直接下单
        elif ordertime == '2':
            while True:
                area = '1_2810_6501_0'  # 地址编码，这里请替换成自己地区的编码
                stockurl = 'http://c0.3.cn/stock?skuId=' + self.pid + '&cat=652,829,854&area=' + area + '&extraParam={%22originid%22:%221%22}'
                resp = s.get(stockurl)
                jsparser = json.loads(resp.text)
                # 33 有货 34 无货
                if jsparser['stock']['StockState'] == 33 and jsparser['stock']['StockStateName'] == '现货':
                    print('库存状态：', jsparser['stock']['StockStateName'])

                    req8 = s.post(submitOrder, data=submit_data)
                    print('正在提交订单...')
                    js1 = json.loads(req8.text)

                    # 判断是否下单成功
                    if js1['success'] == True:
                        print('下单成功!')
                        break
                    else:
                        print('下单失败')
                        # 3秒后重新尝试下单，可自行修改时间间隔
                        time.sleep(3)
                        continue
                elif jsparser['stock']['StockState'] != 33:
                    print('无货，监控中...')
                    time.sleep(3)  # 请酌情修改时间间隔，最少1秒
                    continue

    def coupon_section(self, section):
        def event_func(action):
            r = s.get(couponURL)
            d = pq(r.text)
            content = d("div.content").text()
            print(bcolors.OKGREEN + content)

            if u"已经参加过" in content:
                print("scheduler cancelled")
                scheduler.cancel(action)

        def perform(couponTime, overtime, inc, t, section):
            currentTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(bcolors.HEADER + section + bcolors.OKBLUE + " Coupon Time: ",
                  t, "Current Time:",
                  currentTime + " " + multiprocessing.current_process().name)

            timediff = time.time() - couponTime
            if timediff < (float(overtime) * 60):
                action = scheduler.enter(
                    inc, 0, perform, (couponTime, overtime, inc, t, section))
                event_func(action)

        # 为每一个section开启一个独立进程，运行独立的scheduler
        scheduler = sched.scheduler(time.time, time.sleep)

        print(section)
        incc = float(cfg.get(section, "inc"))
        couponURL = cfg.get(section, "url")
        timeStr = cfg.get(section, "time")
        overtime = cfg.getint(section, "overtime")
        leadtime = cfg.getint(section, "leadtime")
        timeList = timeStr.split(",")

        for t in timeList:
            l = t.split(":")
            hour = l[0]
            minute = l[1]
            # print("enterabs: ", hour, minute)
            couponTime = each_day_time(int(hour), (int(minute) - leadtime), 0)
            scheduler.enterabs(couponTime, 0, perform, (couponTime, overtime,
                                                        incc, t, section))

        scheduler.run()

    def login_by_QR(self):
        # jd login by QR code
        try:
            print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            print(u'{0} > 请打开京东手机客户端，准备扫码登陆:'.format(time.ctime()))

            urls = ('https://passport.jd.com/new/login.aspx',
                    'https://qr.m.jd.com/show', 'https://qr.m.jd.com/check',
                    'https://passport.jd.com/uc/qrCodeTicketValidation')

            self.headers = {
                'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
                'ContentType':
                'text/html; charset=utf-8',
                'Accept-Encoding':
                'gzip, deflate, sdch',
                'Accept-Language':
                'zh-CN,zh;q=0.8',
                'Connection':
                'keep-alive',
            }
            # step 1: open login page
            resp = s.get(urls[0], headers=self.headers)
            if resp.status_code != requests.codes.OK:
                print(u'获取登录页失败: %u' % resp.status_code)
                return False

            # save cookies
            for k, v in resp.cookies.items():
                self.cookies[k] = v

            # step 2: get QR image
            resp = s.get(
                urls[1],
                headers=self.headers,
                cookies=self.cookies,
                params={'appid': 133,
                        'size': 147,
                        't': (time.time() * 1000)})
            if resp.status_code != requests.codes.OK:
                print(u'获取二维码失败: %u' % resp.status_code)
                return False

            # save cookies
            for k, v in resp.cookies.items():
                self.cookies[k] = v

            # save QR code
            image_file = 'qr.png'
            with open(image_file, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=1024):
                    f.write(chunk)

            # scan QR code with phone
            os.system('start ' + image_file)

            # step 3： check scan result
            # mush have
            self.headers['Host'] = 'qr.m.jd.com'
            self.headers['Referer'] = 'https://passport.jd.com/new/login.aspx'

            # check if QR code scanned
            qr_ticket = None
            retry_times = 100
            while retry_times:
                retry_times -= 1
                resp = s.get(
                    urls[2],
                    headers=self.headers,
                    cookies=self.cookies,
                    params={
                        'callback':
                        'jQuery%u' % random.randint(100000, 999999),
                        'appid': 133,
                        'token': self.cookies['wlfstk_smdl'],
                        '_': (time.time() * 1000)
                    })

                if resp.status_code != requests.codes.OK:
                    continue

                n1 = resp.text.find('(')
                n2 = resp.text.find(')')
                rs = json.loads(resp.text[n1 + 1:n2])

                if rs['code'] == 200:
                    print(u'{} : {}'.format(rs['code'], rs['ticket']))
                    qr_ticket = rs['ticket']
                    break
                else:
                    print(u'{} : {}'.format(rs['code'], rs['msg']))
                    time.sleep(3)

            if not qr_ticket:
                print(u'二维码登陆失败')
                return False

            # step 4: validate scan result
            # must have
            self.headers['Host'] = 'passport.jd.com'
            self.headers[
                'Referer'] = 'https://passport.jd.com/uc/login?ltype=logout'
            resp = s.get(
                urls[3],
                headers=self.headers,
                cookies=self.cookies,
                params={'t': qr_ticket}, )
            if resp.status_code != requests.codes.OK:
                print(u'二维码登陆校验失败: %u' % resp.status_code)
                return False

            # login succeed
            self.headers['P3P'] = resp.headers.get('P3P')
            for k, v in resp.cookies.items():
                self.cookies[k] = v

            print(u'登陆成功')
            return True

        except Exception as e:
            print('Exp:', e)
            raise

        return False


def each_day_time(hour, min, sec):
    '''返回当天指定时分秒的时间'''
    struct = time.localtime()
    if hour < struct.tm_hour or (hour == struct.tm_hour and
                                 min <= struct.tm_min):
        day = struct.tm_mday + 1
    else:
        day = struct.tm_mday
    return time.mktime((struct.tm_year, struct.tm_mon, day, hour, min, sec,
                        struct.tm_wday, struct.tm_yday, struct.tm_isdst))


def coupon_process(jd):
    cfgSections = cfg.sections()

    ps = []
    for section in cfgSections:
        p = multiprocessing.Process(
            name=section, target=coupon, args=(jd, section))
        print('Child process %s start.' % section)
        p.start()
        ps.append(p)

    for p in ps:
        p.join()
        print('Child process %s end.' % p.name)


def coupon(jd, section):
    jd.coupon_section(section)


if __name__ == '__main__':

    # jd_user = input('请输入京东账号:')
    # jd_pwd = input('请输入京东密码:')
    # rk_user = input('请输入若快账号:')
    # rk_pwd = input('请输入若快密码:')
    # jd_user = "blurm"
    # jd_pwd = "Shopping4JD"
    jd_user = "504786475"
    jd_pwd = "tulipxiao@@55"
    a = JD(jd_user, jd_pwd)
    a.login_by_QR()
    # a.login()
    coupon_process(a)
    # a.addcart()
    # a.coupon()
    # a.addcart()
    # a.submit()
