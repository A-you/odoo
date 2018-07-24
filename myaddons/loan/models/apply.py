# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import odoolightwf as ltwf
import dingtalk
import datetime


class LoanApply(ltwf.WorkflowModel):
    _name = 'loan.apply'
    _description = u'请款申请'
    _inherit = ['mail.thread']
    _rec_name = 'loan_id'
    _order = 'state,order desc'

    _transitions = [

        ['submit', 'draft', 'file_check', None, None, None, 'do_nothing'],
        ['approve', 'file_check', 'auditing', None, None, 'check_file', 'send_approve_message'],
        ['approve', 'auditing', 'remiting', None, None, None, 'send_approve_message'],
        ['approve', 'remiting', 'approved', None, None, None,
         ['action_remit', 'send_approve_message', 'action_create_sale_order']],

        ['refuse', 'remiting', 'auditing', None, None, None, 'send_refuse_message'],
        ['refuse', 'auditing', 'file_check', None, None, None, 'send_refuse_message'],
        ['refuse', 'file_check', 'draft', None, None, None, 'send_refuse_message'],
        ['reject', 'auditing', 'refused', None, None, None, 'send_reject_message'],

        ['reset', '*', 'draft', None, None, None, 'do_nothing'],
    ]
    _states = [
        ('draft', u'草稿'),
        ('file_check', u'资料审核中'),
        ('auditing', u'总经理审批中'),
        ('remiting', u'财务放款中'),
        ('approved', u'放款完成'),
        ('refused', u'拒绝'),
    ]

    submit = ltwf.trigger('submit', u'提交')
    approve = ltwf.trigger('approve', u'同意')
    # approve1 = ltwf.trigger('approve1', u'确认打款')
    refuse = ltwf.trigger('refuse', u'退回')
    reject = ltwf.trigger('reject', u'拒绝')
    reset = ltwf.trigger('reset', u'重置')

    state = fields.Selection(
        _states, u'状态', default='draft', required=True, readonly=True, track_visibility='onchange')

    active = fields.Boolean(default=True)

    remit_date  = fields.Date(u'打款时间')

    can_show_submit_button = fields.Boolean(compute='_compute_can_show_submit_button', default=True)

    def _compute_can_show_submit_button(self):
        perm_group = self.env.user.has_group('loan.group_loan_kfjl') or self.env.user.has_group(
            'loan.group_loan_manager')
        perm_state = self.state in 'draft'
        self.can_show_submit_button = perm_group and perm_state

    can_show_reset_button = fields.Boolean(compute='_compute_can_show_reset_button', default=True)

    def _compute_can_show_reset_button(self):
        perm_group = self.env.user.has_group('loan.group_loan_manager')
        perm_state = True
        self.can_show_reset_button = perm_group and perm_state

    # can_show_refuse_button = fields.Boolean(compute='_compute_can_show_refuse_button', default=True)
    #
    # def _compute_can_show_refuse_button(self):
    # 	perm_group = self.env.user.has_group('loan.group_loan_cwzj')
    # 	perm_state = self.state in 'auditing'
    # 	self.can_show_refuse_button = perm_group and perm_state

    can_show_reject_button = fields.Boolean(compute='_compute_can_show_reject_button', default=True)

    def _compute_can_show_reject_button(self):
        perm_group = self.env.user.has_group('loan.group_loan_cwzj')
        perm_state = self.state in 'auditing'
        perm_manager = self.env.user.has_group('loan.group_loan_manager')
        self.can_show_reject_button = perm_group and perm_state or perm_manager

    can_show_common_button = fields.Boolean(compute='_compute_can_show_common_button', default=True)

    def _compute_can_show_common_button(self):
        perm_documenter = self.env.user.has_group('loan.group_loan_documenter') and self.state in 'file_check'
        perm_account = self.env.user.has_group('loan.group_loan_account') and self.state in 'remiting'
        perm_cwzj = self.env.user.has_group('loan.group_loan_cwzj') and self.state in 'auditing'
        perm_manager = self.env.user.has_group('loan.group_loan_manager')

        self.can_show_common_button = perm_documenter or perm_cwzj or perm_account or perm_manager

    order = fields.Char(u"请款编号", copy=False, )
    saler_id = fields.Many2one('res.users', ondelete='restrict', string=u'客户经理')
    loan_id = fields.Many2one('loan.loan', ondelete="restrict", string=u"客户姓名", readonly=True)
    borrower_id = fields.Many2one('loan.borrower', default=lambda self: self.loan_id.borrower_id)
    product_id = fields.Many2one('product.product', string=u'分期产品', track_visibility='onchange')

    # product_url = fields.Text(related='product_id.product_tmpl_id.description_purchase', string=u'车型链接',
    #                           default=lambda
    #                               self: self.product_id.product_tmpl_id.description_purchase or 'www.autohome.com')
    product_url = fields.Text(related='product_id.product_tmpl_id.description_purchase', string=u'车型链接', )
    # product_url = fields.Text(related='product_id.product_tmpl_id.description_purchase', string=u'车型链接',
    #                           default=lambda
    #                               self: self.product_id.product_tmpl_id.description_purchase)
    vendor_id = fields.Many2one('res.partner', ondelete='restrict', string="经销商", track_visibility='onchange',
                                domain=[('supplier', '=', 1), ('parent_id', '=', False)], )
    loan_product_id = fields.Many2one('product.product', string=u'分期产品', related='loan_id.product_id')
    loan_vendor_id = fields.Many2one('res.partner', ondelete='restrict', string="经销商", related='loan_id.vendor_id')

    currency_id = fields.Many2one(
        'res.currency', string='Currency')

    finance_id = fields.Many2one('product.product', ondelete='restrict', string=u'金融产品', track_visibility='onchange',
                                 domain="[('product_tmpl_id.categ_id.name','=',u'金融')]")
    total_amount = fields.Float(string=u'资产价值', store=True, readonly=False, track_visibility='onchange')
    reality_apply = fields.Float(string=u'实际请款')
    loans = fields.Float(string=u'贷款本金', track_visibility='onchange')
    contract_rate = fields.Float( string=u'签约利率', store=True, readonly=False,
                                 track_visibility='onchange', group_operator="avg", default=0, )

    repayment_periods_number = fields.Integer(u'还款期数', store=True)

    down_payment = fields.Float(string=u'首付款', compute='_compute_down_payment')
    loansinterest = fields.Float(string=u'贷款本息(额度)', compute='_compute_loansinterest', digits=(4, 2))
    loansinterest_ratio = fields.Float(string=u'贷款本息比例(控制线)', compute='_compute_loansinterest_ratio', digits=(4, 2),
                                       store=True, group_operator="avg", default=0, )
    month_payment = fields.Monetary(string=u'月还款金额', compute='_compute_month_payment', digits=(4, 2))
    bank_rate = fields.Float(string=u'银行利率', compute='_default_value', readonly=True, )

    # 只读字段
    loan_finance_id = fields.Many2one('product.product', ondelete='restrict', string=u'金融产品',
                                      track_visibility='onchange',
                                      related='loan_id.finance_id')
    loan_total_amount = fields.Monetary(string=u'资产价值', related='loan_id.total_amount')
    loan_loans = fields.Monetary(string=u'贷款本金', related='loan_id.loans')
    loan_contract_rate = fields.Float(string=u'签约利率')
    loan_down_payment = fields.Monetary(string=u'首付款', related='loan_id.down_payment')
    loan_loansinterest = fields.Monetary(string=u'贷款本息(额度)', related='loan_id.loansinterest')
    loan_loansinterest_ratio = fields.Float(string=u'贷款本息比例(控制线)', related='loan_id.loansinterest_ratio')
    loan_month_payment = fields.Monetary(string=u'月还款金额', related='loan_id.month_payment')
    loan_bank_rate = fields.Float(string=u'银行利率', related='loan_id.bank_rate', readonly=True, )

    borrower_file_check = fields.Boolean(u'客户资料是否齐全', default=False)
    contract_file_check = fields.Boolean(u'合同书是否齐全', default=False)

    def do_nothing(self):
        pass

    def check_file(self):
        if self.borrower_file_check and self.contract_file_check:
            print self.borrower_file_check
            print self.contract_file_check
            return True
        else:
            print self.borrower_file_check
            print self.contract_file_check
            raise UserError(_(u'资料未全部勾选，不能进行同意操作！'))

    # 设置打款时间
    def action_remit(self):
        # self.remit_date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.remit_date = fields.datetime.strftime(fields.datetime.now(), u'%Y-%m-%d %H:%M%S')
        # self.send_success_message()

    # print self.remit_date

    def send_approve_message(self):

        # 发送消息
        message = ''
        if self.state == 'file_check':
            message = u"资料已审核 通过！"
        elif self.state == 'auditing':
            message = u"总经理已审批 通过！"
        elif self.state == 'remiting':
            message = u"财务放款完成！"
        else:
            return False

        # 组装消息内容
        ctuple = (
            self._description,
            self.loan_id.credit_id.borrower_id.name,
            # self.identity,
            # self.address,
            message,
            fields.datetime.strftime(fields.datetime.utcnow() + datetime.timedelta(hours=8), u'%Y-%m-%d %H:%M:%S'),
        )
        content = u'【%s】 客户姓名：%s，%s  %s' % ctuple
        # content = u'【%s】 客户姓名：%s，电话：%s，身份证号：%s，家庭住址：%s，%s %s' % ctuple

        print content + '  11111'
        # print  borrower_name
        dingtalk.send_dingtalk_message(self, content)

    def send_refuse_message(self):

        # 发送消息
        message = ''
        if self.state == 'file_check':
            message = u"资料已审核 退回"
        elif self.state == 'auditing':
            message = u"总经理已审批 退回"
        elif self.state == 'remiting':
            message = u"财务 退回"
        else:
            return False

        # 组装消息内容
        ctuple = (
            self._description,
            self.loan_id.credit_id.borrower_id.name,
            # self.identity,
            # self.address,
            message,
            fields.datetime.strftime(fields.datetime.utcnow() + datetime.timedelta(hours=8), u'%Y-%m-%d %H:%M:%S'),
        )
        content = u'【%s】 客户姓名：%s，%s。 %s' % ctuple
        # content = u'【%s】 客户姓名：%s，电话：%s，身份证号：%s，家庭住址：%s，%s %s' % ctuple
        dingtalk.send_dingtalk_message(self, content)

    def send_reject_message(self):

        # 发送消息
        message = ''
        if self.state == 'auditing':
            message = u"总经理已审批 拒绝！"
        else:
            return False

        # 组装消息内容
        ctuple = (
            self._description,
            self.loan_id.credit_id.borrower_id.name,
            # self.tag_ids[0].name,
            # self.identity,
            # self.address,
            message,
            fields.datetime.strftime(fields.datetime.utcnow() + datetime.timedelta(hours=8), u'%Y-%m-%d %H:%M:%S'),
        )
        content = u'【%s】 客户姓名：%s，%s。 %s' % ctuple
        # content = u'【%s】 客户姓名：%s，电话：%s，身份证号：%s，家庭住址：%s，%s %s' % ctuple

        dingtalk.send_dingtalk_message(self, content)

    @api.onchange('finance_id')
    def _default_value(self):
        if self.finance_id:
            for attr in self.finance_id.attribute_value_ids:
                # if attr.attribute_id.name == u'签约利率':
                #     self.contract_rate = attr.name
                if attr.attribute_id.name == u'银行利率':
                    self.bank_rate = attr.name
                if attr.attribute_id.name == u'还款期数':
                    self.repayment_periods_number = attr.name
        return

    @api.onchange('total_amount', 'loans')
    def _compute_down_payment(self):
        for x in self:
            x.down_payment = x.total_amount - x.loans

    @api.onchange('total_amount', 'down_payment')
    def _compute_loans(self):
        for x in self:
            x.loans = x.total_amount - x.down_payment

    @api.onchange('total_amount', 'loansinterest')
    def _compute_loansinterest_ratio(self):
        for x in self:
            if x.total_amount <> 0: x.loansinterest_ratio = x.loansinterest / x.total_amount * 100

    @api.onchange('contract_rate', 'loans')
    def _compute_loansinterest(self):
        for x in self:
            x.loansinterest = x.loans * (1 + x.contract_rate / 100)

    @api.onchange('loansinterest', 'repayment_periods_number')
    def _compute_month_payment(self):
        for x in self:
            if x.repayment_periods_number <> 0: x.month_payment = x.loansinterest / x.repayment_periods_number

    @api.model
    def create(self, vals):
        if not vals.get('order'):
            vals['order'] = self.env['ir.sequence'].next_by_code('loan.apply') or '/'
            print vals['order']
        return super(LoanApply, self).create(vals)

    def action_create_sale_order(self):
        for record in self:
            print record.borrower_id
            lists = []
            product_val = {'product_id': record.product_id.id or '',
                           'name': record.total_amount or '',
                           # 'name': record.product_id.name or '',
                           'product_uom_qty': 1,
                           'price_unit': 0,
                           }
            finance_val = {
                'product_id': record.finance_id.id or '',
                'name': record.contract_rate or '',
                'product_uom_qty': 1,
                'price_unit': record.loans or 0,
                # 'price_unit': record.total_amount or 0,

            }
            if product_val['product_id'] != '':
                lists.append((0, 0, product_val))
            if finance_val['product_id'] != '':
                lists.append((0, 0, finance_val))
            val = {
                'partner_id': record.borrower_id.partner_id.id,
                'user_id': record.saler_id.id,
                'state': 'sale',
                'order_line': lists,
            }
            order = self.env['sale.order'].sudo().with_context(
                {'mail_create_nosubscribe': True, }).create(val)
            if self.saler_id:
                order.message_subscribe_users(user_ids=[self.saler_id.id])
            return order

    @api.multi
    def _track_subtype(self, init_values):
        self.ensure_one()
        old_partner_ids = self.message_partner_ids.mapped('id')
        self.message_subscribe(partner_ids=old_partner_ids, subtype_ids=[self.env.ref('mail.mt_comment').id, ],
                               force=True)
        if 'state' in init_values and self.state == 'file_check':
            documenter = self.env.ref('loan.group_loan_documenter')
            documenter_ids = documenter.users.mapped('partner_id.id')
            # self.message_unsubscribe_users(user_ids=zhlr_ids, subtype_ids=[self.env.ref('loan.mt_loan_todo').id, ])
            self.message_subscribe(partner_ids=documenter_ids, subtype_ids=[self.env.ref('loan.mt_apply_todo').id, ],
                                   force=True)
            return 'loan.mt_apply_todo'
            # return 'mail.mt_comment'
        elif 'state' in init_values and self.state == 'auditing':
            cwzj = self.env.ref('loan.group_loan_cwzj')
            cwzj_ids = cwzj.users.mapped('partner_id.id')
            # self.message_unsubscribe_users(user_ids=zhlr_ids, subtype_ids=[self.env.ref('loan.mt_loan_todo').id, ])
            self.message_subscribe(partner_ids=cwzj_ids, subtype_ids=[self.env.ref('loan.mt_apply_todo').id, ],
                                   force=True)
            return 'loan.mt_apply_todo'
        elif 'state' in init_values and self.state == 'remiting':
            account = self.env.ref('loan.group_loan_account')
            account_ids = account.users.mapped('partner_id.id')
            # self.message_unsubscribe_users(user_ids=zhlr_ids, subtype_ids=[self.env.ref('loan.mt_loan_todo').id, ])
            self.message_subscribe(partner_ids=account_ids, subtype_ids=[self.env.ref('loan.mt_apply_todo').id, ],
                                   force=True)
            return 'loan.mt_apply_todo'
        # return 'mail.mt_note'
        return super(LoanApply, self)._track_subtype(init_values)
