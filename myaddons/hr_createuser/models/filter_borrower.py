# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import datetime, timedelta
import psycopg2


class FilterBorrower(models.Model):
	_inherit = 'loan.borrower'

	# def set_condition(self):
	# 	Param = self.env['ir.values'].sudo()
	# 	filter_state = Param.get_default('disable.config', 'yt_appid') or 'draft'
	# 	filter_date = Param.get_default('disable.config', 'filter_dates') or '7'
	#
	# 	self.clear_void_borrower = FilterBorrower.clear_void_borrower(filter_state, filter_date)

	@api.model
	def clear_void_borrower(self):
		# dones = self.search([('state', '=', filter_state), ('create_date', '&gt;=',
		#                                                     time.strftime('%Y-%m-01 00:00:00')),
		#                      ('create_date', '&lt;',
		#                       (context_today() + relativedelta(months=1)).strftime('%Y-%m-01 00:00:00'))])
		# print self
		dones = self.search([('state', '=','draft')])
		dones.write({'active': False})
		return True

	# sql = "select create_date from loan_borrower"
	#
	# @api.model
	# def clear_void_borrower(self):
	# 		dones = self.search([('state', '=', 'draft'),('create_date','&gt;=',
	# 		                                              time.strftime('%Y-%m-01 00:00:00')),
	# 		                     ('create_date','&lt;',
	# 		                      (context_today() + relativedelta(months=1)).strftime('%Y-%m-01 00:00:00'))])
	# 		# print self.create_date
	# 		dones.write({'active': False})
	# 		return True
	#
	# @api.model
	# def clear_void_borrower(self, state, days):
	# 	dones = self.search([('state', '=', state), ('create_date', '&gt;=',
	# 	                                             time.strftime('%Y-%m-01 00:00:00')),
	# 	                     ('create_date', '&lt;',
	# 	                      (context_today() + relativedelta(months=1)).strftime('%Y-%m-01 00:00:00'))])
	# 	dones.write({'active': False})
	# 	return True
