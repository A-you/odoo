# -*- coding: utf-8 -*-

IN_CSC = True
CSC_CLIENT_VERSION = '0.1'
CSC_CLIENT_RELEASE = '20151203'

TD_ONLINE = False
TD_NO_SSL_VERIFY = False
PARTNER_CODE = 'xxx'
PARTNER_KEY = 'xxx'
APP_NAME = 'xxx'

_config = {
    'td_online': TD_ONLINE,
    'td_no_ssl_verify': TD_NO_SSL_VERIFY,
    'partner_code': PARTNER_CODE,
    'partner_key': PARTNER_KEY,
    'app_name': APP_NAME,
}


def get_td_config():
    return _config


def set_td_config(td_online=None, td_no_ssl_verify=None, partner_code=None, partner_key=None, app_name=None, ):
    if td_online:
        _config['td_online'] = td_online
    if td_no_ssl_verify:
        _config['td_no_ssl_verify'] = td_no_ssl_verify
    if partner_code:
        _config['partner_code'] = partner_code
    if partner_key:
        _config['partner_key'] = partner_key
    if app_name:
        _config['app_name'] = app_name
