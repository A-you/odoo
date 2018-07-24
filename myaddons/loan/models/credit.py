# -*- coding: utf-8 -*-

# from odoo import fields, api, models
import datetime
from odoo import api, fields, tools, models, _
import odoolightwf as ltwf

import tempfile
import base64
import os
import re
from odoo.exceptions import ValidationError, Warning
import json
import urllib2
import dingtalk


class LoanCredit(ltwf.WorkflowModel):
	_name = 'loan.credit'
	_description = u'征信查询'
	_rec_name = 'borrower_id'
	_inherit = ['mail.thread']
	_order = 'state desc,order desc'

	# The workflow is set up according to the _states and _transitions attributes.
	# No new objects are created in the database, only the 'state' field (defined later) is used
	# to track the workflow.
	_states = [
		# (<technical name>, <pretty name>),
		('draft', u'草稿'),
		('entering', u'征信录入中'),
		('auditing', u'征信审批中'),
		('re_checking', u'风控审批中'),
		('approved', u'同意'),
		('refused', u'拒绝'),
	]
	# _transitions = [
	#     # [<trigger>, <source>, <dest>, <conditions>, <unless>, <before>, <after>, <prepare>]
	#     ['submit', 'draft', 'entering', None, None, None, 'send_success_message'],
	#     ['submit', 'entering', 'auditing', None, None, None, 'do_nothing'],
	#     ['submit', 'auditing', 're_checking', None, None, None, 'do_nothing'],
	#     ['approve', 'auditing', 'approved', None, None, 'action_create_loan', 'send_success_message'],
	#     ['approve', 're_checking', 'approved', None, None, 'action_create_loan', 'send_success_message'],
	#     ['refuse', 'auditing', 'entering', None, None, None, 'do_nothing'],
	#     ['refuse', 'entering', 'draft', None, None, None, 'send_fail_message'],
	#     ['reject', 're_checking', 'refused', None, None, None, 'send_fail_message'],
	#     # ['reset', '*', 'draft', 'reset_condition', None, None, 'do_nothing'],
	#     ['reset', 'approved', 'draft', 'reset_condition', None, None, 'do_nothing'],
	#     ['reset', 'refused', 'draft', 'reset_condition', None, None, 'do_nothing'],
	# ]
	_transitions = [
		# [<trigger>, <source>, <dest>, <conditions>, <unless>, <before>, <after>, <prepare>]
		['submit', 'draft', 'entering', None, None, None, 'send_success_message'],
		['submit', 'entering', 'auditing', None, None, None, 'do_nothing'],
		['submit', 'auditing', 're_checking', None, None, None, 'do_nothing'],
		['approve', 'auditing', 'approved', None, None, None,
		 ['set_credit_approve_time', 'action_create_loan', 'send_success_message']],
		['approve', 're_checking', 'approved', None, None,
		 ['set_credit_approve_time', 'action_create_loan', 'send_success_message']],
		['refuse', 'auditing', 'entering', None, None, None, 'do_nothing'],
		['refuse', 'entering', 'draft', None, None, None, 'send_fail_message'],
		['reject', 're_checking', 'refused', None, None, None, ['set_credit_approve_time', 'send_fail_message']],
		# ['reset', '*', 'draft', 'reset_condition', None, None, 'do_nothing'],
		['reset', 'approved', 'draft', 'reset_condition', None, None, 'do_nothing'],
		['reset', 'refused', 'draft', 'reset_condition', None, None, 'do_nothing'],
	]

	state = fields.Selection(
		_states, u'状态', default='draft', required=True, readonly=True, track_visibility='onchange')

	submit_enter = ltwf.trigger('submit', u'提交录入')
	submit_audit = ltwf.trigger('submit', u'提交审核')
	submit_re_check = ltwf.trigger('submit', u'提交复审')
	audit_approve = ltwf.trigger('approve', u'审核同意')
	re_check_approve = ltwf.trigger('approve', u'复审同意')
	enter_refuse = ltwf.trigger('refuse', u'录入退回')
	audit_refuse = ltwf.trigger('refuse', u'审核退回')
	reject = ltwf.trigger('reject', u'拒绝')
	reset = ltwf.trigger('reset', u'重置')

	active = fields.Boolean(default=True)

	saler_id = fields.Many2one('res.users', ondelete='restrict', string=u'客户经理', readonly=True,
							   default=lambda self: self.env.uid)
	order = fields.Char(u'编号', copy=False, readonly=True)
	borrower_id = fields.Many2one('loan.borrower', ondelete='restrict', string=u'客户姓名', auto_join=True,required=True)
	credit = fields.Text(u'征信情况', readonly=True, )
	tag_ids = fields.Many2many('res.partner.category', string=u'标签', ondelete='restrict',track_visibility='onchange' )
	# domain=['|', ('active', '=', False), ('active', '=', True)])
	# loan_id = fields.Many2one('loan.loan',u'业务申请')
	loan_count = fields.Integer(u"业务数", compute='_compute_loan_count')

	@api.multi
	def _compute_loan_count(self):
		for credit in self:
			credit.loan_count = self.env['loan.loan'].with_context(active_test=False).sudo().search_count(
				[('credit_id', '=', credit.id)])

	def do_nothing(self):
		pass

	def reset_condition(self):
		"""有相关业务申请，不能重置"""
		# return False
		if self.env['loan.loan'].sudo().search([('credit_id', '=', self.id)]):
			return False
		return True

	def action_create_loan(self):
		if self.tag_ids and self.tag_ids[0].name == u'本人':
			val = {
				'saler_id': self.saler_id.id,
				'state': 'draft',
				'credit_id': self.id,
				'borrower_id': self.borrower_id.id
				# 'co_borrower_ids': [(6, 0, [self.id, ]), ]
			}
			loan = self.env['loan.loan'].sudo().with_context(
				{'mail_create_nosubscribe': True, }).create(val)
			if self.saler_id:
				loan.message_subscribe_users(user_ids=[self.saler_id.id])
			return loan

	@api.model
	def create(self, vals):
		if not vals.get('order'):
			vals['order'] = self.env['ir.sequence'].next_by_code('loan.credit') or '/'
			print vals['order']
		return super(LoanCredit, self).create(vals)

	def _get_assigned_tags(self, assigned_tags):
		return ', '.join([k.name for k in assigned_tags])

	@api.multi
	def write(self, vals):
		old_assigned_tags = self._get_assigned_tags(self.tag_ids)
		super(LoanCredit, self).write(vals)
		new_assigned_tags = self._get_assigned_tags(self.tag_ids)
		if old_assigned_tags != new_assigned_tags:
			self.message_post(
				body="<ul><li>标签：%s <b>&#8594;</b>%s </li></ul>" % (old_assigned_tags, new_assigned_tags))
			# self.message_post(body="<b>关系人：</b> %s &#8594; %s" % (old_assigned_users, new_assigned_users))
		return True

	can_edit_credit = fields.Boolean(compute='_compute_can_edit_credit', default=False)

	def _compute_can_edit_credit(self):
		perm_group = self.env.user.has_group('loan.group_loan_manager')
		perm_state = self.state in 'entering'
		self.can_edit_credit = perm_group and perm_state

	# def _track_subtype(self, init_values):
	#     if 'state' in init_values:
	#         return 'mail.mt_comment'
	#     return False

	# def send_dingtalk_message(self):
	#     print self.state
	#     self.send_message(self)

	def send_success_message(self):

		# 发送消息
		message = ''
		if self.state == 're_checking':
			message = u"风控已审批 通过！"
		elif self.state == 'auditing':
			message = u"主管已审批 通过！"
		elif self.state == 'entering':
			message = u"驻行录入中！"
		else:
			return False

		# 组装消息内容
		ctuple = (
			self._description,
			self.borrower_id.name,
			# self.tag_ids[0].name,
			# self.identity,
			# self.address,
			message,
			fields.datetime.strftime(fields.datetime.utcnow() + datetime.timedelta(hours=8), u'%Y-%m-%d %H:%M:%S'),
		)
		content = u'【%s】 客户姓名：%s，%s。 %s' % ctuple
		# content = u'【%s】 客户姓名：%s，电话：%s，身份证号：%s，家庭住址：%s，%s %s' % ctuple

		dingtalk.send_dingtalk_message(self, content)

	def send_fail_message(self):

		# 发送消息
		message = ''
		if self.state == 're_checking':
			message = u"风控已审批 拒绝！"
		elif self.state == 'auditing':
			message = u"主管已审批 退回！"
		elif self.state == 'entering':
			message = u"驻行录入 退回！"
		else:
			return False

		# 组装消息内容
		ctuple = (
			self._description,
			self.borrower_id.name,
			# self.tag_ids[0].name,
			# self.identity,
			# self.address,
			message,
			# fields.datetime.strftime(fields.datetime.utcnow(), u'%Y-%m-%d %H:%M:%S')
			fields.datetime.strftime(fields.datetime.utcnow() + datetime.timedelta(hours=8), u'%Y-%m-%d %H:%M:%S')
		)
		content = u'【%s】 客户姓名：%s，%s。 %s' % ctuple
		# content = u'【%s】 客户姓名：%s，电话：%s，身份证号：%s，家庭住址：%s，%s %s' % ctuple

		dingtalk.send_dingtalk_message(self, content)

	#
	# class Tag(models.Model):
	#     _name = "loan.credit.tag"
	#     _description = u"征信标签"
	#
	#     name = fields.Char(u'名称', required=True, translate=True)
	#     color = fields.Integer(u'颜色')
	#     active = fields.Boolean(u'状态', default=True)
	#
	#     sequence = fields.Integer(u'顺序')
	#
	#     _sql_constraints = [
	#         ('name_uniq', 'unique (name)', u"标签名已经存在！"),
	#     ]
	# cy0711:增加联系人筛选字段
	# is_contact_show = fields.Boolean(compute='compute_is_contact_show',default=False,)
	is_contact_show = fields.Boolean(u'是否显示该联系人', default=False)
	credit_overdue_time = fields.Date(u'征信过期日期')
	credit_approve_time = fields.Date(u'征信通过时间')

	def compute_is_contact_show(self):
		for record in self:
			print 'depends--------------------------------------'
			if record.tag_ids:
				# cy0710 满足征信未通过的内担保类型的联系人
				if record.state == 'refused' and u'内担保' in record.tag_ids.mapped('name'):
					record.is_contact_show = True
				# cy0710 状态为通过且联系人为非本人
				elif record.state == 'approved' and not u'本人' in record.tag_ids.mapped('name'):
					record.is_contact_show = True
				else:
					record.is_contact_show = False
			else:
				record.is_contact_show = False
			print record.is_contact_show

	# cy: 写入征信通过的时间节点
	def set_credit_approve_time(self):
		for record in self:
			# record.credit_approve_time = fields.datetime.strftime(fields.datetime.now(), u'%Y-%m-%d')
			record.credit_approve_time = fields.datetime.now()
			record.compute_is_credit_overdue()

	# cy:计算征信过期时间
	def compute_is_credit_overdue(self):
		if self.credit_approve_time:
			# print type(self.create_date)
			# from_string直接转化
			approve_time = fields.Datetime.from_string(self.credit_approve_time)
			# 再计算出31天后的时间
			self.credit_overdue_time = approve_time + datetime.timedelta(days=31)

	# cy:该函数在标签/状态改变时触发
	#      判断联系人是否满足 过滤条件
	# @api.depends('tag_ids','state')
	# def compute_is_contact_show(self):
	# 	for record in self:
	# 		print 'depends--------------------------------------'
	# 		if record.tag_ids:
	# 			# cy0710 满足征信未通过的内担保类型的联系人
	# 			if record.state == 'refused' and u'内担保' in record.tag_ids.mapped('name'):
	# 				record.is_contact_show = True
	# 			# cy0710 状态为通过且联系人为非本人
	# 			elif record.state == 'approved' and not u'本人' in record.tag_ids.mapped('name'):
	# 				record.is_contact_show = True
	# 			else:
	# 				record.is_contact_show = False
	# 		print record.is_contact_show
	#
	# # cy: 写入征信通过的时间节点
	# def set_credit_approve_time(self):
	# 	for record in self:
	# 		record.credit_approve_time = fields.datetime.strftime(fields.datetime.now(), u'%Y-%m-%d')
	# 		record.compute_is_credit_overdue()
	#
	# # cy:计算征信过期时间
	# def compute_is_credit_overdue(self):
	# 	if self.credit_approve_time:
	# 		# 将string格式的时间转化为datetime格式
	# 		dtime = datetime.datetime.strptime(self.credit_approve_time, "%Y-%m-%d")
	# 		# 再计算出30天后的时间
	# 		aftertime = dtime + datetime.timedelta(days=31)
	# 		# 再转化格式
	# 		self.credit_overdue_time = fields.datetime.strftime(aftertime, u'%Y-%m-%d')

	@api.multi
	def _track_subtype(self, init_values):
		self.ensure_one()
		old_partner_ids = self.message_partner_ids.mapped('id')
		self.message_subscribe(partner_ids=old_partner_ids, subtype_ids=[self.env.ref('mail.mt_comment').id, ],
							   force=True)
		if 'state' in init_values and self.state == 'entering':
			zhlr = self.env.ref('loan.group_loan_zhlr')
			zhlr_ids = zhlr.users.mapped('partner_id.id')
			# self.message_unsubscribe_users(user_ids=zhlr_ids, subtype_ids=[self.env.ref('loan.mt_loan_todo').id, ])
			self.message_subscribe(partner_ids=zhlr_ids, subtype_ids=[self.env.ref('loan.mt_credit_todo').id, ],
								   force=True)
			return 'loan.mt_credit_todo'
			# return 'mail.mt_comment'
		elif 'state' in init_values and self.state == 'auditing':
			zhzg = self.env.ref('loan.group_loan_zhzg')
			zhzg_ids = zhzg.users.mapped('partner_id.id')
			# self.message_unsubscribe_users(user_ids=zhlr_ids, subtype_ids=[self.env.ref('loan.mt_loan_todo').id, ])
			self.message_subscribe(partner_ids=zhzg_ids, subtype_ids=[self.env.ref('loan.mt_credit_todo').id, ],
								   force=True)
			return 'loan.mt_credit_todo'
		elif 'state' in init_values and self.state == 're_checking':
			fkzj = self.env.ref('loan.group_loan_fkzj')
			fkzj_ids = fkzj.users.mapped('partner_id.id')
			# self.message_unsubscribe_users(user_ids=zhlr_ids, subtype_ids=[self.env.ref('loan.mt_loan_todo').id, ])
			self.message_subscribe(partner_ids=fkzj_ids, subtype_ids=[self.env.ref('loan.mt_credit_todo').id, ],
								   force=True)
			return 'loan.mt_credit_todo'

		# cy0711:
		# 在状态为通过或拒绝的前提下，标签或状态被改变时，更新 is_contact_show字段
		elif self.state in ('approved', 'refused') and ('state' in init_values or 'tag_ids' in init_values):
			self.compute_is_contact_show()

		# return 'mail.mt_note'
		return super(LoanCredit, self)._track_subtype(init_values)
