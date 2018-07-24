# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class LoanUser(models.Model):
    _inherit = 'res.users'

    @api.model
    def create(self, vals):
        user = super(LoanUser, self).create(vals)
        user.partner_id.write({'mobile': user.login})
        return user