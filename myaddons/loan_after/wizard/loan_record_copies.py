# -*- coding: utf-8 -*-
from odoo import  models,fields,api,_
from odoo import  exceptions
import logging

_logger = logging.getLogger(__name__)

class LoanRecordCopies(models.TransientModel):
	_name = 'loan.record.copies'

	copies1 = fields.Boolean(string=u'权证', default=False, track_visibility='onchange')
	copies2 = fields.Boolean(string=u'抵押', default=False, track_visibility='onchange')
	copies3 = fields.Boolean(string=u'保险', default=False, track_visibility='onchange')
	copies4 = fields.Boolean(string=u'面签照', default=False, track_visibility='onchange')
	copies5 = fields.Boolean(string=u'发票', default=False, track_visibility='onchange')
	copies6 = fields.Char(string=u'其他', default='无')

	def _default_sessions(self):
		return self.env['loan.record'].browse(self._context.get('active_ids'))

	loan_record_ids = fields.Many2many('loan.record', string=u'批处理扫描件', default=_default_sessions)

	@api.multi
	def do_mass_update(self):
		self.ensure_one()
		# if not (self.new_deadline or self.new_user_id):
		# 	raise exceptions.ValidationError('No data to update!')
		_logger.debug('批量更新扫描件回件情况%s',
		              self.loan_record_ids.ids)
		vals = {}
		if self.copies1:
			vals['copies1'] = self.copies1
		if self.copies2:
			vals['copies2'] = self.copies2
		if self.copies3:
			vals['copies3'] = self.copies3
		if self.copies4:
			vals['copies4'] = self.copies4
		if self.copies5:
			vals['copies5'] = self.copies5
		if self.copies6:
			vals['copies6'] = self.copies6
		# Mass write values on all selected tasks
		if vals:
			print vals
			self.loan_record_ids.write(vals)
		return True