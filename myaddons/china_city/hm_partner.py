# -*- coding: utf-8 -*-


from odoo import models, fields


class HmPartner(models.Model):
    _inherit = 'res.partner'

    city = fields.Many2one('hm.city', 'city')
    district = fields.Many2one('hm.district', 'district')

class HmEmployee(models.Model):
    _inherit = 'hr.employee'

    city = fields.Many2one('hm.city', 'city')
    district = fields.Many2one('hm.district', 'district')
#
