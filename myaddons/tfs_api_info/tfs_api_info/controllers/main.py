# -*- coding: utf-8 -*-
###########################################################################################
#
#    module name for odoo
#    Copyright (C) 2015 odoo Technology CO.,LTD. (<http://www.tfsodoo.com/>).
#
###########################################################################################
from odoo import http
from odoo.http import request
from odoo.tools.translate import GettextAlias
from odoo.addons.website.controllers.main import *
import util, json, hashlib, urllib, httplib
from datetime import datetime, timedelta
import binascii

_ = GettextAlias()

# 国内正式环境url
server_url = 'open.aichezaixian.com'


class tfs_api_info(http.Controller):
    # 跳转页面路由
    @http.route(['/tfs/api/info'], type='http', auth="public", website=True)
    def tfs_api_info(self, **post):
        values = {}
        app_key = '8FB345B8693CCD00D633786744140938'
        app_script = '2862ecf009f845d5bc76381c1eb5d849'
        user_id = '感知物联网'
        user_password = 'cxygps001'
        imeis = '868120167116315' #设备imei号，多个中间用英文逗号隔开
        # 获取access_token
        access_token = self.get_token('jimi.oauth.token.get', app_key, app_script, user_id, user_password)
        values['access_token'] = access_token
        # 获取账户获取所有子账户信息
        values['get_users'] = self.get_users('jimi.user.child.list',app_key,app_script,access_token, user_id)
        # 获取账户下所有IMEI信息
        values['get_devices'] = self.get_devices('jimi.user.device.list',app_key,app_script,access_token, user_id)
        # 获取账户下所有IMEI的最新定位数据
        values['get_devices_location'] = self.get_devices_location('jimi.user.device.location.list',app_key,app_script,access_token, user_id)
        # 获取IMEI获取最新定位数据
        values['get_devices_location_imei'] = self.get_devices_location_imei('jimi.device.location.get',app_key,app_script,access_token, imeis)
        # 根据IMEI获取设备详细信息
        values['get_devices_imei_info'] = self.get_devices_imei_info('jimi.open.device.getDetails',app_key,app_script,access_token, imeis)
        # 根据IMEI获取轨迹数据
        # 这里的imeis一次只能一个
        values['get_devices_imei_track'] = self.get_devices_imei_track('jimi.device.track.list',app_key,app_script,access_token, imeis,'2018-3-14 11:44:29','2018-3-14 16:44:29')
        return request.render("tfs_api_info.tfs_api_info_template", values)

    # 获取通用参数
    def get_parmse(self, method, app_key):
        parmse = {
            'method': method,  # API接口名称
            'timestamp': (datetime.now() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S'),  # 时间戳
            'app_key': app_key,  # 几米分给客户的APP_KEY
            'sign_method': 'md5',  # 签名方式
            'v': '0.9',  # API版本
            'format': 'json',  # 响应格式
        }
        return parmse

    # 获取accesstoken
    # method:jimi.oauth.token.get
    def get_token(self, method, app_key, app_secret, user_id, user_pwd_md5):
        # 获取通用参数
        parmse = self.get_parmse(method, app_key)
        # 增加私有参数
        parmse['user_id'] = user_id  # 用户ID
        parmse['user_pwd_md5'] = hashlib.md5(user_pwd_md5).hexdigest()  # 用户ID密码的MD5
        parmse['expires_in'] = '60'  # access token的有效期
        # 获取签名
        # 将非空字典键值按ASCII码升序排列，然后拼接起来
        _, prestr = util.params_filter(parmse)
        # 将所拼接的字符串进行MD5运算，并将结果使用十六进制表示
        parmse['sign'] = binascii.b2a_hex(hashlib.md5(app_secret + prestr + app_secret).hexdigest())
        # 访问地址
        request_url = urllib.urlencode(parmse)
        httpsClient = httplib.HTTPConnection(server_url)
        httpsClient.request('POST', '/route/rest', request_url,
                            {"Content-type": "application/x-www-form-urlencoded"})
        ret_json = httpsClient.getresponse().read()
        ret_dict = json.loads(ret_json)
        # 判断返回值
        if ret_dict.get('message') == 'success':
            accessToken = ret_dict.get('result').get('accessToken')
            return accessToken
        else:
            return ret_dict.get('message')

    # 获取账户获取账户下子系统
    # method:jimi.user.child.list
    def get_users(self, method, app_key, app_secret, access_token, target):
        # 获取通用参数
        parmse = self.get_parmse(method, app_key)
        # 增加私有参数
        parmse['access_token'] = access_token  # access_token
        parmse['target'] = target  # 要查询的用户账号
        # 访问地址
        request_url = urllib.urlencode(parmse)
        httpsClient = httplib.HTTPConnection(server_url)
        httpsClient.request('POST', '/route/rest', request_url,
                            {"Content-type": "application/x-www-form-urlencoded"})
        ret_json = httpsClient.getresponse().read()
        ret_dict = json.loads(ret_json)
        # 判断返回值
        if ret_dict.get('message') == 'success':
            res = ''
            for line in ret_dict.get('result'):
                res += line.get('name')+','
            return res
        else:
            return ret_dict.get('message')

    # 获取账户下的所有IMEI信息
    # method:jimi.user.device.list
    def get_devices(self, method, app_key, app_secret, access_token, target):
        # 获取通用参数
        parmse = self.get_parmse(method, app_key)
        # 增加私有参数
        parmse['access_token'] = access_token  # access_token
        parmse['target'] = target  # 要查询的用户账号
        # 访问地址
        request_url = urllib.urlencode(parmse)
        httpsClient = httplib.HTTPConnection(server_url)
        httpsClient.request('POST', '/route/rest', request_url,
                            {"Content-type": "application/x-www-form-urlencoded"})
        ret_json = httpsClient.getresponse().read()
        ret_dict = json.loads(ret_json)
        # 判断返回值
        if ret_dict.get('message') == 'success':
            res = ''
            for line in ret_dict.get('result'):
                res += line.get('deviceName')+','
            return res
        else:
            return ret_dict.get('message')

    # 获取账户下的所有IMEI最新定位信息
    # method:jimi.user.device.location.list
    def get_devices_location(self, method, app_key, app_secret, access_token, target):
        # 获取通用参数
        parmse = self.get_parmse(method, app_key)
        # 增加私有参数
        parmse['access_token'] = access_token  # access_token
        parmse['target'] = target  # 要查询的用户账号
        # 访问地址
        request_url = urllib.urlencode(parmse)
        httpsClient = httplib.HTTPConnection(server_url)
        httpsClient.request('POST', '/route/rest', request_url,
                            {"Content-type": "application/x-www-form-urlencoded"})
        ret_json = httpsClient.getresponse().read()
        ret_dict = json.loads(ret_json)
        # 判断返回值
        if ret_dict.get('message') == 'success':
            res = ''
            for line in ret_dict.get('result'):
                res += line.get('deviceName')+','
            return res
        else:
            return ret_dict.get('message')

    # 根据IMEI获取最新定位数据
    # method:jimi.device.location.get
    def get_devices_location_imei(self, method, app_key, app_secret, access_token, imeis):
        # 获取通用参数
        parmse = self.get_parmse(method, app_key)
        # 增加私有参数
        parmse['access_token'] = access_token  # access_token
        parmse['imeis'] = imeis  # 设备imei号
        # 访问地址
        request_url = urllib.urlencode(parmse)
        httpsClient = httplib.HTTPConnection(server_url)
        httpsClient.request('POST', '/route/rest', request_url,
                            {"Content-type": "application/x-www-form-urlencoded"})
        ret_json = httpsClient.getresponse().read()
        ret_dict = json.loads(ret_json)
        # 判断返回值
        if ret_dict.get('message') == 'success':
            res = ''
            for line in ret_dict.get('result'):
                res += ('('+str(line.get('lat',0))+','+str(line.get('lng',0))+')'+',')
            return res
        else:
            return ret_dict.get('message')

    # 根据IMEI获取设备详细信息
    # method:jimi.open.device.getDetails
    def get_devices_imei_info(self, method, app_key, app_secret, access_token, imeis):
        # 获取通用参数
        parmse = self.get_parmse(method, app_key)
        # 增加私有参数
        parmse['access_token'] = access_token  # access_token
        parmse['imeis'] = imeis  # 设备imei号
        # 访问地址
        request_url = urllib.urlencode(parmse)
        httpsClient = httplib.HTTPConnection(server_url)
        httpsClient.request('POST', '/route/rest', request_url,
                            {"Content-type": "application/x-www-form-urlencoded"})
        ret_json = httpsClient.getresponse().read()
        ret_dict = json.loads(ret_json)
        # 判断返回值
        if ret_dict.get('message') == 'success':
            res = ''
            for line in ret_dict.get('result'):
                res += line.get('deviceName')+','
            return res
        else:
            return ret_dict.get('message')

    # 根据IMEI获取轨迹数据
    # method:jimi.device.track.list
    def get_devices_imei_track(self, method, app_key, app_secret, access_token, imeis, begin_time, end_time):
        # 获取通用参数
        parmse = self.get_parmse(method, app_key)
        # 增加私有参数
        parmse['access_token'] = access_token  # access_token
        parmse['imei'] = imeis  # 设备imei号，只能一个
        parmse['begin_time'] = begin_time  # 开始时间
        parmse['end_time'] = end_time  # 结束时间
        # 访问地址
        request_url = urllib.urlencode(parmse)
        httpsClient = httplib.HTTPConnection(server_url)
        httpsClient.request('POST', '/route/rest', request_url,
                            {"Content-type": "application/x-www-form-urlencoded"})
        ret_json = httpsClient.getresponse().read()
        ret_dict = json.loads(ret_json)
        # 判断返回值
        if ret_dict.get('message') == 'success':
            res = ''
            for line in ret_dict.get('result'):
                res += ('('+str(line.get('lat',0))+','+str(line.get('lng',0))+')'+',')
            return res
        else:
            return ret_dict.get('message')
