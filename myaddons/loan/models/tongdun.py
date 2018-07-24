# -*- coding: utf-8 -*-
import urllib
import json
import pycurl
import certifi
from io import BytesIO

# 默认为调用测试环境服务
# 如果需要调用线上接口服务，请移除下面一项的注释
TD_ONLINE = True

# 如果需要关闭客户端证书校验，移除下面一项的注释
TD_NO_SSL_VERIFY = False

td_auth_keys = {
    'partner_code': '',
    'partner_key': '',
    'app_name': '',
}

hostname = 'api.tongdun.cn' if TD_ONLINE else 'apitest.tongdun.cn'

TD_HOST_BASE = 'https://{0}'.format(hostname)
TD_CLOUD_AUTH = 'partner_code={0}&partner_key={1}&app_name={2}'.format(td_auth_keys['partner_code'],
                                                                       td_auth_keys['partner_key'],
                                                                       td_auth_keys['app_name'])

IN_CSC = True
CSC_CLIENT_VERSION = '0.1'
CSC_CLIENT_RELEASE = '20151203'


# class TongDun(object):

# /**
#  *  贷前申请准入提交
#  *  param: params array()
#  *
#  *  return array(
#  *      success: 提交是否成功
#  *      reason_code: success为false的情况下对应错误码,调用失败时包含此字段。
#  *      reason_desc: 错误详情描述，调用失败时包含此字段
#  *      report_id: 贷前申请风险报告编号，调用成功时包含此字段。
#  *  )
#  */
def pre_loan_apply(params):
    return td_invoke_service('/preloan/apply/v5', 'POST', params)


# /**
#  *  贷前申请准入报告查询
#  *  param: report_id 准入申请时候得到的报告编号
#  *
#  *  return array(
#  *       success: 提交是否成功
#  *       reason_code: success为false的情况下对应错误码,调用失败时包含此字段。
#  *       reason_desc: 错误详情描述，调用失败时包含此字段
#  *       final_score: 风险分数
#  *       final_decision: 风险结果
#  *       report_id: 报告编号
#  *       device_type: 设备类型,申请准入传入token_id或black_box时才有
#  *       proxy_info: 代理信息,申请准入传入ip_address时才有，
#  *       apply_time: 扫描时间,UNIX时间戳,毫秒级
#  *       report_time: 报告时间,UNIX时间戳,毫秒级
#  *       device_info: 设备环境信息,申请准入传入token_id或black_box时才有，
#  *       geo_ip: 地理位置信息,申请准入传入ip_address时才有，
#  *       geo_trueip: 真实地理位置信息,申请准入传入token_id或black_box时才有
#  *       risk_items: 扫描出来的风险项
#  *  )
#  */
def pre_loan_report(report_id):
    return td_invoke_service('/preloan/report/v9', 'GET', {"report_id": report_id})

    # /**
    #  * params 请求参数
    #  * timeout 超时时间
    #  * connection_timeout 连接超时时间
    #  */


def td_invoke_service(path, method, params, timeout=2000, connection_timeout=2000):
    options = td_build_options(path, method, params, timeout, connection_timeout)
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


def td_build_options(path, method, params, timeout=2000, connection_timeout=2000):
    url = td_build_url(path)
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


def td_build_url(path):
    url = TD_HOST_BASE + path + '?' + TD_CLOUD_AUTH
    return url
