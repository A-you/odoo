# coding=utf-8

import urllib2
import json
import math, base64
from ..routes import robot

from odoo import models, fields, api, time
from odoo.http import request
# import datetime

_baidu_urlString = "http://api.map.baidu.com/geocoder/v2/?location={0}&coordtype=bd09ll&output=json&pois=1&ak=qaq2UuZhwjRG4G1i18CY3RnOkSGfft4t"
_baidu_urlConvert2 = "http://api.map.baidu.com/geoconv/v1/?coords={0}&from=1&to=5&ak=qaq2UuZhwjRG4G1i18CY3RnOkSGfft4t"


@robot.location
def location(message):
    print message.latitude, message.longitude
    convertUrl = _baidu_urlConvert2.format(str(message.longitude) + ',' + str(message.latitude))
    convertOpen = urllib2.urlopen(convertUrl)
    convertResult = json.loads(convertOpen.read().decode("utf-8"))
    lat = convertResult['result'][0]['x']
    lon = convertResult['result'][0]['y']
    print lon, lat
    url2 = _baidu_urlString.format(str(lon) + ',' + str(lat))
    open2 = urllib2.urlopen(url2)
    result2 = json.loads(open2.read().decode("utf-8"))
    print result2['result']['formatted_address']
    url = result2['result']['formatted_address'] + '\n' + result2['result']['pois'][0]['addr'] + \
          result2['result']['pois'][0][
              'direction'] + result2['result']['pois'][0]['distance'] + u'米'

    info = {
        'user_id': request.env()['wx.user'].sudo().search([('openid', '=', message.source)]).id,
        # 'loc_time': fields.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        # 'loc_time': fields.datetime.strftime(fields.datetime.now(),"%Y-%m-%d %H:%M:%S"),
        # 'loc_time': fields.datetime.now(),
        'loc_coordinate': str(lon) + ',' + str(lat),
        'loc_address': url

    }
    url_map = request.env()['user.loc'].sudo().create(info).loc_url
    # request.env()['user.loc'].sudo().search([])
    return ''
    # return u'欢迎回家！'
