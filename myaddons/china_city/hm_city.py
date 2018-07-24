# -*- coding: utf-8 -*-

from odoo import models, fields


class HmCity(models.Model):
    _name = 'hm.city'

    name = fields.Char('name')
    state = fields.Many2one('res.country.state', 'state')


class HmDistrict(models.Model):
    _name = "hm.district"

    name = fields.Char('name')
    city = fields.Many2one('hm.city', 'city')


# class HmPartner(models.Model):
#     _inherit = 'res.partner'
#
#     city = fields.Many2one('hm.city', 'city'),
#     district = fields.Many2one('hm.district', 'district'),
