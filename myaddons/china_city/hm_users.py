# -*- coding: utf-8 -*-

from odoo import models, fields


class HmUsers(models.Model):
    _inherit = 'res.users'

    city = fields.Many2one('hm.city', 'city')
