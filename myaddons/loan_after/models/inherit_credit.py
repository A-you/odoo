# -*- coding: utf-8 -*-
import odoolightwf as ltwf
from odoo import api,models,fields

class InheritCredit(ltwf.WorkflowModel):
	_inherit = "loan.credit"

	credit_time = fields.Date(string=u'查询时间',readonly=True)
	# @api.model
	# def submit_audit(self):
	# 	credit_time = fields.datetime.strftime(fields.datetime.now(),u'%Y-%m-%d')
	# 	# self.credit_time = fields.datetime.strftime(fields.datetime.now(),u'%Y-%m-%d')
	# 	return super(InheritCredit,self).create(credit_time)