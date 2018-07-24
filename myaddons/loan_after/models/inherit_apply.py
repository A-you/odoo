# -*- coding: utf-8 -*-
from odoo import api,models,fields
import odoolightwf as ltwf

class CreateAfter(ltwf.WorkflowModel):
	_inherit = "loan.apply"
	# _name = 'loan.apply.inherit'
	# _inherit = ''

	@api.multi
	def action_create_basis(self):
		for record in self:
			relation_partners = self.loan_id.relation_ids.mapped('borrower_id.partner_id.id')
			relation_descriptions = ''
			for relation in record.loan_id.relation_ids:
				borrower = relation.borrower_id
				relation_descriptions += u"姓名：{}，与主贷人关系：{}，手机号码：{}，身份证号：{}，住址：{}。\n".format(
					borrower.name, ','.join(relation.tag_ids.mapped('name')), borrower.phone, borrower.identity,
					borrower.address)
			attachment_ids = self.env['ir.attachment'].search(['|',('res_model','=','loan.borrower'),('res_model','=','loan.loan'),\
			                                                   ('res_id','=',record.borrower_id.id),'|','|',('res_field','=',None),('res_field','=','frontimage'),('res_field','=','backimage')]).mapped('id')
			# atts = attachment_ids.copy()
			val = {
				# 流程中不可改动信息
				'product_id':record.product_id.id,
				'borrower_id': record.borrower_id.id,
				'credit_id':record.loan_id.credit_id.id,
				'loan_id': record.loan_id.id,
				'apply_id': record.id,
				'partner_id': record.borrower_id.partner_id.id,
				'finance_id': self.finance_id.id,
				# 客户录入中信息
				'phone': record.borrower_id.phone,
				'identity': record.borrower_id.identity,
				'address': record.borrower_id.address,
				'frontimage': record.borrower_id.frontimage,
				'backimage': record.borrower_id.backimage,
				# 征信查询中信息
				'credit_time': record.loan_id.credit_id.credit_approve_time,
				'credit': record.loan_id.credit_id.credit,
				# 业务申请中信息
				'maddress': record.loan_id.homing_address,
				'homing_time': record.loan_id.homing_time,
				'homing_result': record.loan_id.homing_result,
				'homing_id': record.loan_id.homing_id.id,
				'phoning_id': record.loan_id.phoning_id.id,
				'phoning_time': record.loan_id.phoning_time,
				'phoning_result': record.loan_id.phoning_result,
				'GPS_suggest': record.loan_id.GPS_suggest,
				'loan_suggest': record.loan_id.loan_suggest,
				'relation_ids': [(6, 0, relation_partners)],
				'relation_descriptions': relation_descriptions,
				'attachment_ids': [(6,0,attachment_ids)],
				# 请款中的信息
				'total_amount': record.total_amount,
				'loans': record.loans,
				'contract_rate': record.contract_rate,
				'vendor_id': record.vendor_id.id,
				'bank_date': record.remit_date,
				# 客户经理
				'saler_id': record.borrower_id.saler_id.id,
			}
			# print val
			# print val['attachment_ids']
			# print val['contract_euribor']

			self.env['loan.record'].sudo().create(val)