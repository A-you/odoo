# -*- coding: utf-8 -*-
import urllib2, urllib
import json
import requests
import pycurl
import certifi
from io import BytesIO
# import StringIO
import conf


class TongDun(object):

    def __init__(self, td_online, td_no_ssl_verify, partner_code, partner_key, app_name):
        self.IN_CSC = True
        self.CSC_CLIENT_VERSION = '0.1'
        self.CSC_CLIENT_RELEASE = '20151203'
        self._td_online = td_online
        self._td_no_ssl_verify = td_no_ssl_verify
        self._partner_code = partner_code
        self._partner_key = partner_key
        self._app_name = app_name

        self.hostname = 'api.tongdun.cn' if self._td_online else 'apitest.tongdun.cn'
        self.TD_HOST_BASE = 'https://{0}'.format(self.hostname)
        self.TD_CLOUD_AUTH = 'partner_code={0}&partner_key={1}&app_name={2}'.format(partner_code, partner_key, app_name)

        conf.set_td_config(td_online, td_no_ssl_verify, partner_code, partner_key, app_name)

    def pre_loan_apply(self, params):
        # info =conf.get_td_config()
        # print info
        return self.td_invoke_service('/preloan/apply/v5', 'POST', params)

    def pre_loan_report(self, report_id):
        return self.td_invoke_service('/preloan/report/v9', 'GET', {"report_id": report_id})

    # /**
    #  * params 请求参数
    #  * timeout 超时时间
    #  * connection_timeout 连接超时时间
    #  */

    def td_invoke_service(self, path, method, params, timeout=2000, connection_timeout=2000):
        options = self.td_build_options(path, method, params, timeout, connection_timeout)
        buffer = BytesIO()
        ch = pycurl.Curl()
        if options.get('CURLOPT_POSTFIELDS'): ch.setopt(pycurl.POSTFIELDS, options['CURLOPT_POSTFIELDS'])
        ch.setopt(pycurl.URL, options['CURLOPT_URL'])
        ch.setopt(pycurl.CONNECTTIMEOUT, options['CURLOPT_CONNECTTIMEOUT_MS'])
        ch.setopt(pycurl.TIMEOUT, options['CURLOPT_TIMEOUT_MS'])
        ch.setopt(pycurl.CAINFO, certifi.where())
        ch.setopt(pycurl.WRITEFUNCTION, buffer.write)
        # buffer = BytesIO()
        ret = {}
        print options['CURLOPT_URL']
        ch.perform()
        # print ch.getinfo(pycurl.HTTP_CODE)
        if ch.getinfo(pycurl.HTTP_CODE) != 200:
            # // 错误处理，按照同盾接口格式fake调用结果
            ret = {
                'success': False,
                'reason_code': '9',
                'reason_desc': u'网络存在错误',
            }
        else:
            ret = buffer.getvalue()
        ch.close()
        print json.loads(ret)
        return json.loads(ret)

    def td_build_options(self, path, method, params, timeout=2000, connection_timeout=2000):
        url = self.td_build_url(path)
        options = {
            'CURLOPT_RETURNTRANSFER': 1,  # // 获取请求结果
            # // -----------请确保启用以下两行配置 - -----------
            'CURLOPT_SSL_VERIFYPEER': 1,  # // 验证证书
            'CURLOPT_SSL_VERIFYHOST': 2,  # // 验证主机名
        }
        if (method.upper() == "POST"):
            options['CURLOPT_POST'] = 1
            options['CURLOPT_POSTFIELDS'] = urllib.urlencode(params)
        else:
            url = url + '&' + urllib.urlencode(params)

        options['CURLOPT_URL'] = url

        if 'CURLOPT_TIMEOUT_MS':
            options['CURLOPT_NOSIGNAL'] = 1
            options['CURLOPT_TIMEOUT_MS'] = timeout
        else:
            options['CURLOPT_TIMEOUT'] = ceil(timeout / 1000)

        if 'CURLOPT_CONNECTTIMEOUT_MS':
            options['CURLOPT_CONNECTTIMEOUT_MS'] = connection_timeout
        else:
            options['CURLOPT_CONNECTTIMEOUT'] = ceil(connection_timeout / 1000)

        return options

    def td_build_url(self, path):
        url = self.TD_HOST_BASE + path + '?' + self.TD_CLOUD_AUTH
        return url
