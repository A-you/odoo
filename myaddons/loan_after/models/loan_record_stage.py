# -*- coding: utf-8 -*-
from odoo import models,fields,api,_

class LoanRecordStage(models.Model):
	_name = 'loan.record.stage'
	_description = u'贷后阶段设置'
	_order = 'sequence,name,id'

	name = fields.Char(
							string=u'阶段名称',
							copy=False,
							default='未抵押',
							index=True,
							redonly=False,
							required=True,
							# states = {'done': [('readonly',False)]},
							)
	fold = fields.Boolean('Folded')
	sequence = fields.Integer('Sequence')

	customer_ids = fields.One2many(
	        'loan.record',
	        'stage_id',
	        'Record in this stage')


