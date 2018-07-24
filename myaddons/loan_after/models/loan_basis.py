# -*- coding: utf-8 -*-
from odoo import fields,api,models,_
import tempfile
import os
import base64
import TencentYoutuyun
import time
import datetime
import re
import math
from odoo.exceptions import ValidationError, Warning

class LoanRecord(models.Model):
	_name = 'loan.record'
	_inherit = ['mail.thread']
	_rec_name = 'apply_id'
	_order = 'order desc'


	# 看板视图
	color = fields.Integer('Color Index')
	priority = fields.Selection([('0', 'Low'), ('1', 'Normal'), ('2', 'High')], 'Priority', default='1')
	kanban_state = fields.Selection([('normal', 'In Progress'), ('blocked', 'Blocked'), ('done', 'Read for next stage')],'Kanban State', default='normal')
	stage_id = fields.Many2one('loan.record.stage', u'阶段',group_expand='_read_group_stage_ids',track_visibility='onchange')

	@api.model
	def _read_group_stage_ids(self, stages, domain, order):
		stage_ids = self.env['loan.record.stage'].search([])
		print stage_ids
		return stage_ids

	order = fields.Char(string='档案编号',copy=False,readony=True)
	partner_id = fields.Many2one('res.partner', '关联伙伴', ondelete='restrict', )
	borrower_id = fields.Many2one(
		'loan.borrower','客户录入',ondelete='set null', readonly=True, )
	credit_id = fields.Many2one(
		'loan.credit','征信申请',ondelete='set null', readonly=True, )
	loan_id = fields.Many2one(
		'loan.loan', '业务申请', ondelete='set null', store=True,
		readonly=True, )
	apply_id = fields.Many2one('loan.apply', '请款申请',readonly=True)

	customer_name = fields.Char(related='partner_id.name',store=True,string=u'客户姓名')
	elseaddress = fields.Char(string=u'联系地址',related='partner_id.street')
	# sex = fields.Char(string=u'性别', related='partner_id.title.name')
	sex = fields.Char(string=u'性别',compute='_compute_loan_record_sex')
	work_unit = fields.Char(string=u'工作单位',related='partner_id.function')

	#loan.borrower拷贝过来字段
	identity = fields.Char(string=u'身份证号码')
	phone = fields.Char(string=u'电话')
	address = fields.Char(string=u'户口住址')
	frontimage = fields.Binary(u"身份证正面", attachment=True)
	backimage = fields.Binary(u"身份证反面", attachment=True)

	credit_time=fields.Date(string=u'征信查询时间')
	credit= fields.Text(string=u'征信情况')

	# loan.loan中拷贝过来字段
	maddress = fields.Char(string=u'家访地址',store=True)
	homing_time = fields.Date(string=u'家访日期',store=True)
	homing_result = fields.Text(string=u'家访结论',store=True)
	# 新增字段
	homing_id = fields.Many2one('res.users', ondelete='restrict', string="家访专员",
	                            domain=[('groups_id.name', '=', 'E 家访专员'), ], track_visibility='onchange')
	phoning_id = fields.Many2one('res.users', ondelete='restrict', string="电审专员",
	                             domain=[('groups_id.name', '=', 'F 电审专员'), ], track_visibility='onchange')
	phoning_time = fields.Date(string=u'电审日期',track_visibility='onchange')
	phoning_result = fields.Text(string=u'电审结论' )
	relation_ids = fields.Many2many('res.partner', 'loanrecord_partner_rel', 'record_id', 'partner_id',string='  ')
	relation_descriptions = fields.Text(string='  ')
	GPS_suggest = fields.Text(string=u'GPS安装意见', track_visibility='onchange')
	loan_suggest = fields.Text(string=u'贷款意见', track_visibility='onchange')

	# loan.apply中拷贝过来字段
	total_amount = fields.Float(u'资产价值',rack_visibility='onchange')
	loans = fields.Float(string=u'贷款本金',track_visibility='onchange')
	contract_rate = fields.Float(u'签约利率',track_visibility='onchange',)
	vendor_id = fields.Many2one('res.partner', ondelete='restrict', string="经销商", track_visibility='onchange',
	                            domain=[('supplier', '=', 1), ('parent_id', '=', False)], )
	# 万一客户经理离职，允许删除用户，考虑保存到数据库
	saler_id = fields.Many2one('res.users', ondelete='set null', string=u'客户经理')
	saler_name = fields.Char(string=u'客户经理',related='saler_id.name',store=True)
	saler_phone = fields.Char(string=u'客户经理电话',related='saler_id.login',store=True,)

	product_id = fields.Many2one('product.product',ondelete='restrict', string=u'分期产品', track_visibility='onchange')

	age = fields.Char(string=u'年龄', compute='_compute_borrower_age')

	#金融产品可能会随时间更改，考虑保存到数据库
	finance_id = fields.Many2one('product.product', ondelete='restrict', string=u'金融产品', track_visibility='onchange',
	                             domain="[('product_tmpl_id.categ_id.name','=',u'金融')]")
	finance_name = fields.Char(string=u'金融产品',related='finance_id.name',store=True)
	repayment_periods_number = fields.Integer(string=u'还款期数',compute='_default_value')

	# 根据签约利率及相关信息计算,银行利率可能会更变，保存数据库作参考
	bank_rate = fields.Float(string=u'银行利率',related='apply_id.loan_bank_rate',store=True,track_visibility='onchange')
	or_loansinterest = fields.Float(string=u'本息合计',compute='_compute_or_loansinterest',track_visibility='onchange',)
	loansinterest_ratio = fields.Float(string=u'贷款本息比例(控制线)',compute='_compute_after_loansinterest_ratio',digits=(5,3))
	down_payment = fields.Float(string=u'首付款',compute='_compute_down_payment',digits=(5,3))
	month_payment = fields.Float(string=u'月还款金额',compute='_compute_month_payment',)
	# month_payment = fields.Monetary(string=u'月还款金额',compute='_compute_month_payment', digits=(4, 2))
	first_payment = fields.Char(string=u'首月还款',compute='_compute_first_payment')

	# 银行放款就等于本息合计
	bank_card = fields.Binary(u'银行卡', attachment=True,)
	information_attachment = fields.Many2many('ir.attachment', compute='_get_attachment_ids', string=u'附件', )
	finance_state = fields.Char(string=u'财务资料状态',compute='_onchange_finance_stage',search='_search_finance_state')
	loansinterest = fields.Char(string=u'银行放款金额',track_visibility='onchange')
	bank_date = fields.Datetime(string=u'银行放款时间',track_visibility='onchange')
	pay_client = fields.Char(string=u'放款客户金额',track_visibility='onchange')
	pay_account = fields.Char(string=u'放款客户账号',track_visibility='onchange')
	cardholder = fields.Char(string=u'账户持卡人',track_visibility='onchange')
	advance_payment = fields.Char(string=u'垫款金额',track_visibility='onchange')
	advance_date = fields.Date(string=u'垫款时间',track_visibility='onchange')
	security_cost = fields.Char(string=u'担保费',track_visibility='onchange')
	basis_rate = fields.Char(string=u'基准利率',track_visibility='onchange')
	finance_stage = fields.Boolean(string=u'财务资料完成',compute='_compute_finance_stage',default=False,track_visibility='onchange')

	# credit_id = fields.Many2one('loan.credit','credit',string='征信结果')
	pledge_state = fields.Char(string=u'抵押状态',compute='_onchange_pledge_case')
	pledge_case = fields.Boolean(string=u'是否抵押',default=False)
	pledge_date = fields.Datetime(string=u'抵押时间')
	collect_date = fields.Datetime(string=u'回件时间')
	collect_key = fields.Boolean(string=u'车钥匙是否收取', default=False)
	overdue_num = fields.Integer(string=u'逾期次数')

	# 以下是抵押所需材料  原件
	original1 = fields.Boolean(string=u'大本',default=False,track_visibility='onchange')
	original2 = fields.Boolean(string=u'商业险', default=False,track_visibility='onchange')
	original3 = fields.Boolean(string=u'交强险', default=False,track_visibility='onchange')
	original4 = fields.Boolean(string=u'交税证明', default=False,track_visibility='onchange')
	original5 = fields.Boolean(string=u'发票', default=False,track_visibility='onchange')
	original6 = fields.Char(string=u'其他', default='无')
	original_stage = fields.Boolean(string=u'原件已齐',default=False,readonly=True,compute='_compute_original_stage',track_visibility='onchange')
	original_time = fields.Date(string=u'原件回齐时间',compute='_compute_original_time')

	#一下是复印件所有材料
	copies1 = fields.Boolean(string=u'权证', default=False,track_visibility='onchange')
	copies2 = fields.Boolean(string=u'抵押', default=False,track_visibility='onchange')
	copies3 = fields.Boolean(string=u'保险', default=False,track_visibility='onchange')
	copies4 = fields.Boolean(string=u'面签照', default=False,track_visibility='onchange')
	copies5 = fields.Boolean(string=u'发票', default=False,track_visibility='onchange')
	copies6 = fields.Char(string=u'其他', default='无')
	copies_stage = fields.Boolean(string=u'扫描件已齐',default =False,readonly=True, compute='_compute_copies_stage',track_visibility='onchange')
	copies_time = fields.Date(string=u'扫描件回齐时间', compute='_compute_copies_time')
	attachment_ids = fields.Many2many('ir.attachment',string=u'附件')




#xml中限制只读，不能打开tree视图
	linkman = fields.One2many('res.partner',string=u'  ',related='partner_id.child_ids')

	doc_count = fields.Integer(compute='_compute_attached_docs_count', string="附件数量")




	# 统计文件/图片数量 方法
	def _compute_attached_docs_count(self):
		Attachment = self.env['ir.attachment']
		for rectify in self:
			rectify.doc_count = Attachment.search_count([('res_model', '=', 'loan.credit'), ('res_id', 'in', 'credit_id'),'|',('res_field','=',None),('res_field','=','frontimage')])


	@api.multi
	def attachment_tree_view(self):
		self.ensure_one()
		domain = [('res_model', '=', 'loan.record'), ('res_id', 'in', self.ids),('res_field','=','frontimage')]
		print self.ids
		print type(self.ids)
		print self.id
		print self._name
		return {
			'domain': domain,
			'name': _('附件浏览'),
			'res_model': 'ir.attachment',
			'type': 'ir.actions.act_window',
			'view_id': False,
			'view_mode': 'kanban,tree,form',
			'view_type': 'form',
			'limit': 80,
			'context': "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id)
		}


	# 识别银行卡
	def set_API(self):
		Param = self.env['ir.values'].sudo()
		appid = Param.get_default('loan.config.settings', 'yt_appid') or '10124678'
		secret_id = Param.get_default('loan.config.settings',
		                              'yt_secret_id') or 'AKID1whKl2PCLOGxSmrtfQDtRp253saMpXrz'
		secret_key = Param.get_default('loan.config.settings',
		                               'yt_secret_key') or '7d5NYdXIsHVXSHzWv9Fh0BD3jFYklbGj'
		userid = Param.get_default('loan.config.settings', 'yt_userid') or '1227400499'
		end_point = Param.get_default('loan.config.settings',
		                              'yt_end_point') or TencentYoutuyun.conf.API_YOUTU_END_POINT
		# appid =  '10140891'
		# secret_id = 'AKIDGUCl9TBmfNzQgkOP7kDVcYIsIXbitZEi'
		# secret_key = 'Smxy66yiIhw2zlMlz2xhGnFYgeT7dyAC'
		# userid =  '582838918'
		# end_point = TencentYoutuyun.conf.API_YOUTU_END_POINT
		self.youtu = TencentYoutuyun.YouTu(appid, secret_id, secret_key, userid, end_point)

	@api.onchange('bank_card')
	def _pay_account(self):
		self.ensure_one()
		if not self.bank_card:
			return
		data = base64.decodestring(self.bank_card)
		fobj = tempfile.NamedTemporaryFile(delete=False)
		bname = fobj.name
		fobj.write(data)
		fobj.close()
		try:
			self.set_API()
			bank_cards = self.youtu.creditcardocr(bname, data_type=0, )
			print bank_cards["items"][0]['itemstring']
			self.pay_account = bank_cards["items"][0]['itemstring']
		except Exception:
			raise Warning(_(u'API配置错误，请联系管理员！！'))
		finally:
			# delete the file when done
			os.unlink(bname)



	def _compute_borrower_age(self):
		for x in self:
			if x.identity:
				cur = datetime.datetime.now()
				get_year = int(cur.year)
				get_month = int(cur.month)
				get_day = int(cur.day)
				year = int(x.identity[6:10])
				month = int(x.identity[10:12])
				day = int(x.identity[12:14])
				# print get_day
				# print day
				if get_year > year:
					if get_month > month:
						code_year = get_year - year
						code_month = get_month - month
						age = '%s岁%s个月' % (code_year, code_month)
						x.age = age
					elif get_month < month:
						code_year = get_year - year - 1
						code_month = get_month - month + 12
						age = '%s岁%s个月' % (code_year, code_month)
						x.age = age
					elif get_month == month:
						if get_day> day:
							code_year = get_year -year
							code_day = get_day -day
							age = '%s岁零%s天' % (code_year,code_day)
							x.age = age
						elif get_day<day:
							code_year = get_year -year
							code_day = day -get_day
							age = '%s岁差%s天' % (code_year,code_day)
							x.age = age
						elif get_day ==day:
							code_year =get_year - year
							age = '今天是%s岁生日' %(code_year)
							x.age = age
						else:
							return
					else:
						return
				else:
					return
			else:
				return

	def _compute_loan_record_sex(self):
		for x in self:
			if x.identity:
				num = int(x.identity[16:17])
				print num
				if (num % 2) ==0:
					x.sex = '女'
				else:
					x.sex ='男'
			else:
				return

#定义隐藏字段控制财务管理写的权限
	can_edit_finance = fields.Boolean(compute='_compute_can_edit_finance',default=False)

	def _compute_can_edit_finance(self):
		perm_group1 = self.env.user.has_group('loan.group_loan_cashier')
		perm_group2 = self.env.user.has_group('base.group_system')
		self.can_edit_finance =perm_group1 or perm_group2

#定义隐藏字段控制市场管理写的权限
	can_edit_market = fields.Boolean(compute = '_compute_can_edit_market',default=False)

	def _compute_can_edit_market(self):
		perm_group1 = self.env.user.has_group('loan_after.group_loan_record_market')
		perm_group2 = self.env.user.has_group('base.group_system')
		self.can_edit_market = perm_group1 or perm_group2


	@api.model
	def create(self, vals):
		if not vals.get('order'):
			vals['order'] = self.env['ir.sequence'].next_by_code('loan.record') or '/'
			# print vals['order']
		return super(LoanRecord,self).create(vals)

    #金融产品方法
	@api.onchange('finance_id')
	def _default_value(self):
		if self.finance_id:
			for attr in self.finance_id.attribute_value_ids:
				if attr.attribute_id.name == u'还款期数':
					self.repayment_periods_number = attr.name
					print self.repayment_periods_number
		return

	@api.onchange('total_amount','loans')
	def _compute_down_payment(self):
		for x in self:
			x.down_payment = x.total_amount -  x.loans

	@api.onchange('loans','contract_rate')
	def _compute_or_loansinterest(self):
		for x in self:
			# print x.loans
			# print x.contract_euribor
			x.or_loansinterest = x.loans * (1+ x.contract_rate / 100)

	@api.onchange('total_amoun','loans','contract_rate')
	def _compute_after_loansinterest_ratio(self):
		for x in self:
			if x.total_amount <> 0 : x.loansinterest_ratio = x.loans*(1+x.contract_rate/100)/x.total_amount*100

	@api.onchange('or_loansinterest','repayment_periods_number')
	def _compute_month_payment(self):
		for x in self:
			if x.repayment_periods_number <>0: x.month_payment = math.floor(x.or_loansinterest/x.repayment_periods_number)

	@api.onchange('or_loansinterest','repayment_periods_number')
	def _compute_first_payment(self):
		for x in self:
			if x.repayment_periods_number <>0:
				a = x.or_loansinterest/x.repayment_periods_number
				b = math.floor(x.or_loansinterest/x.repayment_periods_number)
				c = (a - b) * x.repayment_periods_number
				print c
				x.first_payment = b + c

	#下面是判断金融方案中选项是否都勾起
	@api.depends('loansinterest',
	              'bank_date',
	              'pay_client',
	              'pay_account',
	              'cardholder',
	              'advance_payment',
	              'advance_date',
	              'security_cost')
	def _compute_finance_stage(self):
		for x in self:
			# print '111'
			if x.loansinterest and\
					x.bank_date and\
					x.pay_client and\
					x.pay_account and\
					x.cardholder and\
					x.advance_payment and\
					x.advance_date and\
					x.security_cost :
				x.finance_stage = True

	@api.depends('finance_stage')
	def _onchange_finance_stage(self):
		for x in self:
			if x.finance_stage:
				x.finance_state = '已完成'
			else:

				x.finance_state = '未完成'

	def _search_finance_state(self,operator,value):
		return [('finance_state',operator,value)]

	@api.multi
	def action_edit_finance(self):
		self.ensure_one()
		return {
			'name': '财务资料补充',
			'res_model': 'loan.record',
			'type': 'ir.actions.act_window',
			'src_model' :'loan.record',
			'res_id': self.id,
			'view_id': self.env.ref('loan_after.edit_loan_record_finance_form').id,
			'view_mode': 'form',
			'view_type': 'form',
			'target': 'new',
		}

	@api.multi
	def action_edit_bank_num(self):
		self.ensure_one()
		return {
			'name': '银行卡补录',
			'res_model': 'loan.record',
			'type': 'ir.actions.act_window',
			'src_model': 'loan.record',
			'res_id': self.id,
			'view_id': self.env.ref('loan_after.edit_loan_record_bank_num_form').id,
			'view_mode': 'form',
			'view_type': 'form',
			'target': 'new',
		}

	@api.multi
	def action_edit_pledge_case(self):
		self.ensure_one()
		return {
			'name': '抵押确认',
			'res_model': 'loan.record',
			'type': 'ir.actions.act_window',
			'src_model': 'loan.record',
			'res_id': self.id,
			'view_id': self.env.ref('loan_after.view_loan_record_pledge_case_form').id,
			'view_mode': 'form',
			'view_type': 'form',
			'target': 'new',
		}

	@api.multi
	def action_edit_original_record(self):
		self.ensure_one()
		return {
			'name': '原件记录',
			'res_model': 'loan.record',
			'type': 'ir.actions.act_window',
			'src_model': 'loan.record',
			'res_id': self.id,
			'view_id': self.env.ref('loan_after.view_loan_record_original_record_form').id,
			'view_mode': 'form',
			'view_type': 'form',
			'target': 'new',
		}

	@api.multi
	def action_edit_copies_record(self):
		self.ensure_one()
		return {
			'name': '扫描件记录',
			'res_model': 'loan.record',
			'type': 'ir.actions.act_window',
			'src_model': 'loan.record',
			'res_id': self.id,
			'view_id': self.env.ref('loan_after.view_loan_record_copies_record_form').id,
			'view_mode': 'form',
			'view_type': 'form',
			'target': 'new',
		}

     #抵押情况方法
	# pledge_state = fields.Char(string=u'抵押状态')
	@api.onchange('pledge_case')
	def _onchange_pledge_case(self):
		for x in self:
			if x.pledge_case:
				# print '111'
				x.pledge_state = '已完成'
				# print x.pledge_state
			else:
				# print '222'
				x.pledge_state=  '未完成'
				# print x.pledge_state
		return

	@api.onchange('original1','original2','original3','original4','original5')
	def _compute_original_stage(self):
		for x in self:
			x.original_stage = x.original1 and x.original2 and x.original3 and x.original4 and x.original5

	@api.depends('original_stage')
	def _compute_original_time(self):
		for x in self:
			# print x.original_stage
			if x.original_stage :
				x.original_time = fields.datetime.strftime(fields.datetime.now(),u'%Y-%m-%d %H:%M%S')
				break

	@api.onchange('copies1','copies2','copies3','copies4','copies5')
	def _compute_copies_stage(self):
		for x in self:
			# print '3333'
			x.copies_stage = x.copies1 and x.copies2 and x.copies3 and x.copies4 and x.copies5

	@api.depends('copies_stage')
	def _compute_copies_time(self):
		for x in self:
			if x.copies_stage:
				x.copies_time = fields.datetime.strftime(fields.datetime.now(),u'%Y-%m-%d %H:%M%S')

	def _get_attachment_ids(self):
		att_model = self.env['ir.attachment']  # 获取附件模型
		for obj in self:
			query = [('res_model', '=', self._name), ('res_id', '=', obj.id)]  # 根据res_model和res_id查询附件
			obj.information_attachment = att_model.search(query)  # 取得附件list
