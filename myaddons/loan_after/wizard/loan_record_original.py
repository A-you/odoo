# -*- coding: utf-8 -*-
from odoo import  models,fields,api,_
from odoo import  exceptions
import logging

_logger = logging.getLogger(__name__)

class LoanRecordOriginal(models.TransientModel):
	_name = 'loan.record.original'
	# _order = 'order desc'

	# order = fields.Char(string='档案编号', copy=False, readony=True)
	# apply_id = fields.Many2one('loan.apply', string=u'客户姓名', readonly=True)
	# identity = fields.Char(string=u'身份证号码', readonly=True)
	# phone = fields.Char(string=u'电话', readonly=True)
	# saler_id = fields.Char(string=u'客户经理', readonly=True)

	original1 = fields.Boolean(string=u'大本', default=False, track_visibility='onchange')
	original2 = fields.Boolean(string=u'商业险', default=False, track_visibility='onchange')
	original3 = fields.Boolean(string=u'交强险', default=False, track_visibility='onchange')
	original4 = fields.Boolean(string=u'交税证明', default=False, track_visibility='onchange')
	original5 = fields.Boolean(string=u'发票', default=False, track_visibility='onchange')
	original6 = fields.Char(string=u'其他', default='无')

	def _default_sessions(self):
		return self.env['loan.record'].browse(self._context.get('active_ids'))

	loan_record_ids = fields.Many2many('loan.record', string=u'批处理原件', default=_default_sessions)

	@api.multi
	def do_mass_update(self):
		self.ensure_one()
		# if not (self.new_deadline or self.new_user_id):
		# 	raise exceptions.ValidationError('No data to update!')
		_logger.debug('批量更新原件回件情况%s',
		              self.loan_record_ids.ids)
		vals = {}
		if self.original1:
			vals['original1'] = self.original1
		if self.original2:
			vals['original2'] = self.original2
		if self.original3:
			vals['original3'] = self.original3
		if self.original4:
			vals['original4'] = self.original4
		if self.original5:
			vals['original5'] = self.original5
		if self.original6:
			vals['original6'] = self.original6
		# Mass write values on all selected tasks
		if vals:
			self.loan_record_ids.write(vals)
		return True
