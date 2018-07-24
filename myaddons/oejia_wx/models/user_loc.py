# coding=utf-8

import logging
import werkzeug

from odoo import models, fields, api
from ..controllers import client
from openerp.http import request
from openerp.exceptions import ValidationError
from ..rpc import corp_client


def urlplus(url, params):
    return werkzeug.Href(url)(params or None)


class user_loc(models.Model):
    _name = 'user.loc'
    _description = u'微信用户地理位置'
    _rec_name = 'user_id'

    user_id = fields.Many2one(
        'wx.user', string=u'微信用户',
        # optional:
        ondelete='set null',
        context={},
        domain=[],
    )
    # user_name = fields.Char(u'昵称')
    loc_time = fields.Datetime(u'定位时间',default=fields.Datetime.now)
    loc_coordinate = fields.Char(u'经纬度')
    loc_address = fields.Char(u'地址')
    loc_url = fields.Char(compute='baidu_map_link', string='地图')

    @api.onchange('loc_coordinate')
    def baidu_map_img(self, zoom=18, width=500, height=500):
        # country_name = self.country_id and self.country_id.name or ''
        # state_name = self.state_id and self.state_id.name or ''
        # city_name = self.city or ''
        # street_name = self.street or ''
        # street2_name = self.street2 or ''
        for record in self:
            loc = record.loc_coordinate or ''
            # print loc
            params = {
                # 'markers': '%s' % street2_name,
                # 'center': '%s%s%s%s' % (country_name, state_name, city_name, street_name),
                'center': '%s' % loc,
                'markers': '%s' % loc,
                'height': "%s" % height,
                'width': "%s" % width,
                'zoom': zoom,
                'copyright': 1,
                'ak': 'qaq2UuZhwjRG4G1i18CY3RnOkSGfft4t',

            }
            # http://lbsyun.baidu.com/index.php?title=static
            record.loc_url = urlplus('http://api.map.baidu.com/staticimage/v2', params)

    @api.onchange('loc_coordinate')
    def baidu_map_link(self):
        for record in self:
            loc = record.loc_coordinate or ''
            # partner_name = self.name
            # city_name = self.city or ''
            # street2_name = self.street2 or ''
            params = {
                'location': '%s' % loc,
                'output': 'html',
                'coord_type': 'bd09ll',
                'src': 'odoo',
            }
            # http://lbsyun.baidu.com/index.php?title=uri
            record.loc_url = urlplus('http://api.map.baidu.com/geocoder', params)
