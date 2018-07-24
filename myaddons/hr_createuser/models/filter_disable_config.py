# -*- coding: utf-8 -*-
from odoo import api, fields, models


class BillsConfig(models.TransientModel):
	_name = 'bills.config.setting'
	_inherit = 'res.config.settings'

	filter_state = fields.Char('状态设置',
	                           default=lambda self: self.env['ir.values'].sudo().get_default('disable.config',
                                                                                         'filter_state') or '草稿')
	filter_date = fields.Integer('时间设置',
	                              default=lambda self: self.env['ir.values'].sudo().get_default('disable.config',
                                                                                         'filter_dates') or '7')

	@api.multi
	def set_default_filter_state(self):
		check = self.env.user.has_group('base.group_system')
		Values = check and self.env['ir.values'].sudo() or self.env['ir.values']
		for config in self:
			Values.set_default('bills.config.setting','filter_state',config.filter_state)

	@api.multi
	def set_default_filter_date(self):
		check = self.env.user.has_group('base.group_system')
		Values = check and self.env['ir.values'].sudo() or self.env['ir.values']
		for config in self:
			Values.set_default('bills.config.setting','filter_date',config.filter_date)
