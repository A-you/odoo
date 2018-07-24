# -*- coding: utf-8 -*-
from odoo import models,fields,api,_
import odoolightwf as ltwf

class LoanPledge(ltwf.WorkflowModel):
	_name = 'loan.pledge'
	_description = u'抵押管理'
	_inherit = ['mail.thread']
	_order = 'state,order desc'


