# -*- coding: utf-8 -*-
from odoo import models,fields,api,_
from odoo import exceptions
import logging

_logger = logging.getLogger(__name__)

class LoanRecordFinance(models.TransientModel):
	_name = 'loan.record.finance'
	_order = 'order desc'

	order = fields.Char(string='档案编号', copy=False, readony=True)
	apply_id = fields.Many2one('loan.apply', string=u'客户姓名', readonly=True)
	identity = fields.Char(string=u'身份证号码', readonly=True)
	phone = fields.Char(string=u'电话', readonly=True)
	saler_id = fields.Char(string=u'客户经理', readonly=True)

	new_deadline = fields.Date('Deadline to Set')
	new_user_id = fields.Many2one('res.users', string='Responsible to Set')
	# loansinterest = fields.Char(string=u'银行放款金额', track_visibility='onchange')
	bank_date = fields.Datetime(string=u'银行放款时间', track_visibility='onchange')
	advance_date = fields.Date(string=u'垫款时间', track_visibility='onchange')
	@api.multi
	def do_mass_update(self):
		self.ensure_one()
		# if not (self.new_deadline or self.new_user_id):
		# 	raise exceptions.ValidationError('No data to update!')
		_logger.debug('更新财务数据%s',
		              self.loan_record_ids.ids)
		vals = {}
		if self.bank_date:
			vals['bank_date'] = self.bank_date
		if self.new_deadline:
		    vals['advance_date'] = self.advance_date
		# if self.new_user_id:
		    # vals['user_id'] = self.new_user_id
		# Mass write values on all selected tasks
		if vals:
		    self.loan_record_ids.write(vals)
		return True

	@api.multi
	def _reopen_form(self):
		self.ensure_one()
		return {
			'type': 'ir.actions.act_window',
			'res_model':self._name,
			'res_id': self.id,
			'view_mode': 'form',
			'view_type': 'form',
			'target': 'new',
		}

	@api.multi
	def do_populate_tasks(self):
		self.ensure_one()
		Task = self.env['loan.record']
		open_tasks = Task.search([('phone', '=', '13595623124')])
		# Fill the wizard Task list with all tasks
		self.loan_record_ids = open_tasks
		# reopen wizard form on same wizard record
		return self._reopen_form()


	def _default_sessions(self):
		return self.env['loan.record'].browse(self._context.get('active_ids'))

	loan_record_ids = fields.Many2many('loan.record', string=u'多对多', default=_default_sessions)
	# session_ids = fields.Many2many('openacademy.session',
	#                                string="Sessions", required=True, default=_default_sessions)
	# attendee_ids = fields.Many2many('res.partner', string="Attendees")

	# @api.multi
	# def subscribe(self):
	# 	for session in self.session_ids:
	# 		session.attendee_ids |= self.attendee_ids
	# 	return {}



