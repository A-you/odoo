# -*- coding: utf-8 -*-
import datetime
from odoo import api, fields, models, _
import odoolightwf as ltwf
import dingtalk
import tongdun
import time


class Loan(ltwf.WorkflowModel):
    _name = 'loan.loan'
    _description = u'业务申请'
    _inherit = ['mail.thread']
    _rec_name = 'credit_id'
    _order = 'state,order desc'

    _transitions = [
        ['submit', 'draft', 'homing', None, None, None, 'send_jfzg_message'],
        ['approve', 'homing', 'phoning', None, None, None, ['send_approve_message', 'do_nothing']],
        ['approve', 'phoning', 'auditing', None, None, None, ['send_approve_message', 'do_nothing']],
        ['approve', 'auditing', 'approved', None, None, None, ['send_approve_message', 'action_create_apply']],
        ['refuse', 'homing', 'draft', None, None, None, 'send_refuse_message'],
        ['refuse', 'phoning', 'homing', None, None, None, ['send_refuse_message', 'send_jfzg_message']],
        ['refuse', 'auditing', 'phoning', None, None, None, 'send_refuse_message'],
        ['reject', 'auditing', 'refused', None, None, None, 'send_reject_message'],
        ['reset', '*', 'draft', None, None, None, 'do_nothing'],
    ]
    _states = [
        ('draft', u'草稿'),
        ('homing', u'上门调查中'),
        ('phoning', u'电话审核中'),
        ('auditing', u'风控审批中'),
        ('approved', u'同意'),
        ('refused', u'拒绝'),
    ]

    state = fields.Selection(
        _states, u'状态', default='draft', required=True, readonly=True, track_visibility='onchange')

    active = fields.Boolean(default=True)

    order = fields.Char(u"编号", copy=False, readonly=True)
    # 增加一个操作人员字段，以便于过滤记录，在状态流转后方法内实施动态分配（随机、平均、指定人）
    operator_id = fields.Many2one('res.users', ondelete='restrict', string="当前操作员", readonly=True, )
    homing_id = fields.Many2one('res.users', ondelete='restrict', string="家访专员",
                                domain=[('groups_id.name', '=', 'E 家访专员'), ], track_visibility='onchange')
    # domain=[('groups_id.name', 'in', ['loan.group_loan_jfzy',]),], )
    homing_time = fields.Date(string=u'家访日期', required=False, track_visibility='onchange')
    homing_address = fields.Char(string=u'家访地址', required=False, track_visibility='onchange')
    homing_result = fields.Text(string=u'家访结论', required=False, )

    phoning_id = fields.Many2one('res.users', ondelete='restrict', string="电审专员",
                                 domain=[('groups_id.name', '=', 'F 电审专员'), ], track_visibility='onchange')
    phoning_time = fields.Date(string=u'电审日期', required=False, track_visibility='onchange')
    phoning_result = fields.Text(string=u'电审结论', required=False, )
    phoning_opt1 = fields.Boolean(u'购车人夫妻收入情况', )
    phoning_opt2 = fields.Boolean(u'主贷人工作真实性', )
    phoning_opt3 = fields.Boolean(u'房屋大小，目前房价', )
    phoning_opt4 = fields.Boolean(u'在哪买的车，首付多少', )
    phoning_opt5 = fields.Boolean(u'是否购车自用', )
    phoning_opt6 = fields.Boolean(u'贷款金额多少', )
    phoning_opt7 = fields.Boolean(u'如有责任是否愿意承担', )

    identity = fields.Char(string=u'身份证号码',related='credit_id.borrower_id.identity')
    age = fields.Char(string=u'年龄',compute='_compute_borrower_age')
    def _compute_borrower_age(self):
        for x in self:
            if x.identity:
                cur = datetime.datetime.now()
                get_year = int(cur.year)
                get_month = int(cur.month)
                year = int(x.identity[6:10])
                month = int(x.identity[10:12])
                # print age
                # print get_year
                # print get_month
                # print year
                # print month
                if get_year>year:
                    if get_month >=month:
                        code_year = get_year - year
                        code_month = get_month - month
                        age = '%s岁%s月'%(code_year,code_month)
                        x.age = age
                        # print code_year
                        # print code_month
                    elif get_month< month:
                        code_year = get_year - year -1
                        code_month = get_month - month + 12
                        age = '%s岁%s月' % (code_year, code_month)
                        x.age = age
            else:
                return

    GPS_suggest = fields.Text(string=u'GPS安装意见', track_visibility='onchange')
    loan_suggest = fields.Text(string=u'贷款意见', track_visibility='onchange')

    credit_id = fields.Many2one('loan.credit', ondelete="restrict", string="客户姓名", readonly=True,
                                track_visibility='onchange')
    borrower_id = fields.Many2one('loan.borrower', default=lambda self: self.credit_id.borrower_id)

    relation_ids = fields.Many2many('loan.credit', 'loan_co_borrower_rel', 'loan_id', 'credit_id',
                                    string=u"关系人" )

    saler_id = fields.Many2one('res.users', ondelete='restrict', string=u'客户经理', readonly=True,
                               default=lambda self: self.env.uid, track_visibility='onchange')
    # product_id = fields.Many2one('loan.product', ondelete='restrict', string=u'信用卡分期产品', track_visibility='onchange')

    currency_id = fields.Many2one('res.currency', string='Currency')
    finance_id = fields.Many2one('product.product', ondelete='restrict', string=u'金融产品', track_visibility='onchange',
                                 domain="[('product_tmpl_id.categ_id.name','=',u'金融')]")
    # finance_id1 = fields.Many2one('product.product', ondelete='restrict', string=u'金融产品', track_visibility='onchange')
    total_amount = fields.Monetary(string=u'资产价值', track_visibility='onchange')
    down_payment = fields.Monetary(string=u'首付款', compute='_compute_down_payment', track_visibility='onchange')
    loans = fields.Monetary(string=u'贷款本金', track_visibility='onchange')
    loansinterest = fields.Monetary(string=u'贷款本息(额度)', compute='_compute_loansinterest', digits=(4, 2))
    loansinterest_ratio = fields.Float(string=u'贷款本息比例(控制线)', compute='_compute_loansinterest_ratio', digits=(4, 2),
                                       store=True, group_operator="avg", default=0, track_visibility='onchange')
    month_payment = fields.Monetary(string=u'月还款金额', digits=(4, 2), compute='_compute_month_payment')
    contract_rate = fields.Float(compute='_default_value', string=u'签约利率', store=True, readonly=False,
                                 group_operator="avg", default=0,
                                 track_visibility='onchange')
    bank_rate = fields.Float(compute='_default_value', string=u'银行利率', readonly=True, )
    repayment_periods_number = fields.Integer(u'还款期数', store=True)

    # finance_attribute_value_ids = fields.Float(related='finance_id1.attribute_value_ids', string=u'金融信息', readonly=True, )

    doc_count = fields.Integer(compute='_compute_attached_docs_count', string="附件数量")

    # 统计文件/图片数量 方法
    def _compute_attached_docs_count(self):
        Attachment = self.env['ir.attachment']
        for rectify in self:
            rectify.doc_count = Attachment.search_count([('res_model', '=', 'loan.loan'), ('res_id', 'in', self.ids)])

    @api.multi
    def attachment_tree_view(self):
        self.ensure_one()
        domain = [('res_model', '=', 'loan.loan'), ('res_id', 'in', self.ids)]
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

    @api.onchange('finance_id')
    def _default_value(self):
        if self.finance_id:
            for attr in self.finance_id.attribute_value_ids:
                if attr.attribute_id.name == u'签约利率':
                    self.contract_rate = attr.name
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

    submit = ltwf.trigger('submit', u'提交')  # submit_
    approve = ltwf.trigger('approve', u'批准')
    refuse = ltwf.trigger('refuse', u'退回')
    reject = ltwf.trigger('reject', u'拒绝')
    reset = ltwf.trigger('reset', u'重置')

    def do_nothing(self):
        pass

    # For conditions and unless methods, the docstring is used as part of the error
    # message when a transition is attempted but conditions are not met.
    def valid_phone(self):
        """需要有效的电话号码"""
        return self.phone and bool(len(self.phone))

    @api.model
    def create(self, vals):
        if not vals.get('order'):
            vals['order'] = self.env['ir.sequence'].next_by_code('loan.loan') or '/'
            print vals['order']
        return super(Loan, self).create(vals)

    def _get_assigned_users_names(self, assigned_users):
        return ', '.join([k.borrower_id.name for k in assigned_users])

    @api.multi
    def write(self, vals):
        old_assigned_users = self._get_assigned_users_names(self.relation_ids)
        old_homing_id = self.homing_id
        rec = super(Loan, self).write(vals)
        new_assigned_users = self._get_assigned_users_names(self.relation_ids)
        new_homing_id = vals.get('homing_id')
        if old_assigned_users != new_assigned_users:
            self.message_post(
                body="<ul><li>关系人：%s <b>&#8594;</b>%s </li></ul>" % (old_assigned_users, new_assigned_users))
            # self.message_post(body="<b>关系人：</b> %s &#8594; %s" % (old_assigned_users, new_assigned_users))
        if old_homing_id and new_homing_id and old_homing_id != new_homing_id:
            self.send_jfzy_message(old_homing_id)
            # print vals.get('homing_id')
        elif not old_homing_id and new_homing_id:
            self.send_jfzy_message()
        return rec

    product_id = fields.Many2one('product.product', u'分期产品', track_visibility='onchange',
                                 domain="[('product_tmpl_id.categ_id.name','=',u'汽车')]")

    product_url = fields.Text(related='product_id.product_tmpl_id.description_purchase', string=u'车型链接', default='')

    # firm = fields.Many2one('loan.car.firm', u'车商', track_visibility='onchange')
    # line = fields.Many2one('loan.car.line', u'车系', track_visibility='onchange')
    # car = fields.Many2one('loan.car.name', u'车名', track_visibility='onchange')
    # rn：考虑用系统自有伙伴代替经销商
    vendor_id = fields.Many2one('res.partner', ondelete='restrict', string="经销商", track_visibility='onchange',
                                domain=[('supplier', '=', 1), ('parent_id', '=', False)], )

    # saler_id = fields.Many2one('loan.saler', ondelete='restrict', string="经销商", track_visibility='onchange')

    # @api.onchange('firm')
    # def _clear_line_car(self):
    #     self.line = ''
    #     self.car = ''
    #
    # @api.onchange('line')
    # def _clear_car(self):
    #     self.car = ''

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

    can_show_reject_button = fields.Boolean(compute='_compute_can_show_reject_button', default=True)

    def _compute_can_show_reject_button(self):
        perm_group = self.env.user.has_group('loan.group_loan_fkzj')
        perm_state = self.state in 'auditing'
        self.can_show_reject_button = perm_group and perm_state

    can_show_common_button = fields.Boolean(compute='_compute_can_show_common_button', default=True)

    def _compute_can_show_common_button(self):
        perm_jf = (self.env.user.has_group('loan.group_loan_jfzy') or self.env.user.has_group(
            'loan.group_loan_jfzg')) and self.state in 'homing'
        perm_ds = (self.env.user.has_group('loan.group_loan_dszy') or self.env.user.has_group(
            'loan.group_loan_dszg')) and self.state in 'phoning'
        perm_fkzj = self.env.user.has_group('loan.group_loan_fkzj') and self.state in 'auditing'
        # perm_cwzj = self.env.user.has_group('loan.group_loan_cwzj') and self.state in 'approving'
        perm_manager = self.env.user.has_group('loan.group_loan_manager')

        self.can_show_common_button = perm_jf or perm_ds or perm_fkzj or perm_manager

    can_edit_suggest = fields.Boolean(compute='_compute_can_edit_suggest', default=False)

    def _compute_can_edit_suggest(self):
        perm_group = self.env.user.has_group('loan.group_loan_fkzj') or self.env.user.has_group(
            'loan.group_loan_manager')
        self.can_edit_suggest = perm_group

    # def _track_subtype(self, init_values):
    #     if 'state' in init_values:
    #         return 'mail.mt_comment'
    #     # return False
    #     return 'mail.mt_note'

    def send_approve_message(self):

        # 发送消息
        message = ''
        if self.state == 'auditing':
            message = u"风控已审批 通过！"
        elif self.state == 'homing':
            message = u"已完成家访！"
        elif self.state == 'phoning':
            message = u"已完成电审！"
        else:
            return False

        # 组装消息内容
        ctuple = (
            self._description,
            self.credit_id.borrower_id.name,
            # self.tag_ids[0].name,
            # self.identity,
            # self.address,
            message,
            fields.datetime.strftime(fields.datetime.utcnow() + datetime.timedelta(hours=8), u'%Y-%m-%d %H:%M:%S'),
        )
        content = u'【%s】 客户姓名：%s，%s。 %s' % ctuple
        # content = u'【%s】 客户姓名：%s，电话：%s，身份证号：%s，家庭住址：%s，%s %s' % ctuple

        dingtalk.send_dingtalk_message(self, content)

    def send_refuse_message(self):

        # 发送消息
        message = ''
        if self.state == 'auditing':
            message = u"风控已审批 退回！"
        elif self.state == 'homing':
            message = u"家访 退回！"
        elif self.state == 'phoning':
            message = u"电审 退回！"
        else:
            return False

        # 组装消息内容
        ctuple = (
            self._description,
            self.credit_id.borrower_id.name,
            # self.tag_ids[0].name,
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
            message = u"风控已审批 拒绝！"
        else:
            return False

        # 组装消息内容
        ctuple = (
            self._description,
            self.credit_id.borrower_id.name,
            # self.tag_ids[0].name,
            # self.identity,
            # self.address,
            message,
            fields.datetime.strftime(fields.datetime.utcnow() + datetime.timedelta(hours=8), u'%Y-%m-%d %H:%M:%S'),
        )
        content = u'【%s】 客户姓名：%s，%s。 %s' % ctuple
        # content = u'【%s】 客户姓名：%s，电话：%s，身份证号：%s，家庭住址：%s，%s %s' % ctuple

        dingtalk.send_dingtalk_message(self, content)

        # 发送钉钉消息给家访专员

    def send_jfzy_message(self, old_homing_id=None):
        # 组装消息内容
        message1 = ''
        res_old = ''
        if old_homing_id:
            message1 = u"家访主管已撤销分配给你的任务，请知晓"
            ctuple = (
                self._description,
                self.credit_id.borrower_id.name,
                message1,
                fields.datetime.strftime(fields.datetime.utcnow() + datetime.timedelta(hours=8), u'%Y-%m-%d %H:%M:%S'),
            )
            content = u'【%s】 客户姓名：%s，%s  %s' % ctuple
            res_old = dingtalk.send_dingtalk_message(self, content, 'jfzy', old_homing_id)
            if res_old and res_old['errcode'] == 0:
                self.env.user.notify_info('已通知前调查员任务取消')

        message = u"家访主管已分派调查任务，请尽快处理"
        ctuple = (
            self._description,
            self.credit_id.borrower_id.name,
            message,
            fields.datetime.strftime(fields.datetime.utcnow() + datetime.timedelta(hours=8), u'%Y-%m-%d %H:%M:%S'),
        )
        content = u'【%s】 客户姓名：%s，%s  %s' % ctuple
        print content

        res = dingtalk.send_dingtalk_message(self, content, 'jfzy')
        print 'res: %s' % (res)
        if res and res['errcode'] == 0:
            self.env.user.notify_info('分派任务消息已发送至 %s' % (self.homing_id.name))
        else:
            self.env.user.notify_warning('分派通知消息发送失败，请自行通知调查员，并联系管理员反馈问题')

        # 发送钉钉消息给家访主管

    def send_jfzg_message(self):
        # 组装消息内容
        if self.state == 'draft':
            message = u"客户经理已提交业务单，请家访主管分派调查员"
        else:
            message = u"业务单已被打回，请家访主管重新分派调查员"
        ctuple = (
            self._description,
            self.credit_id.borrower_id.name,
            message,
            fields.datetime.strftime(fields.datetime.utcnow() + datetime.timedelta(hours=8), u'%Y-%m-%d %H:%M:%S'),
        )
        content = u'【%s】 客户姓名：%s，%s  %s' % ctuple
        print content

        dingtalk.send_dingtalk_message(self, content, 'jfzg')

    @api.multi
    def action_exchange_borrower(self):
        if self.state not in ['draft', 'homing', 'phoning', ]:
            return self.env.user.notify_warning(u'该状态下，不能互换！')
        if self.relation_ids:
            for id in self.relation_ids:
                # print self.relation_ids[0], self.credit_id
                for tag in id.tag_ids:
                    if u'共债人' == tag.name:
                        tmp_tag = self.credit_id.tag_ids
                        self.credit_id.tag_ids = id.tag_ids
                        id.tag_ids = tmp_tag

                        self.borrower_id = id.borrower_id

                        tmp_id = self.credit_id
                        self.credit_id = id
                        self.relation_ids -= id
                        self.relation_ids |= tmp_id
                        return True
        return self.env.user.notify_warning(u'无共债人，不能互换！')
        # TODO: 需要考虑例外情况，还要补充完善的对列表的控制

    @api.multi
    def action_bigdata_credit(self):
        pass

    def action_create_apply(self):
        val = {
            'vendor_id': self.vendor_id.id,
            'state': 'draft',
            'loan_id': self.id,
            'borrower_id': self.borrower_id.id,
            # 'firm': self.firm.id,
            # 'line': self.line.id,
            # 'car': self.car.id,
            'product_id': self.product_id.id,
            'saler_id': self.saler_id.id,
            'total_amount': self.total_amount,
            'finance_id': self.finance_id.id,
            'loans': self.loans,
            'reality_apply':self.loans,
            'loan_contract_rate':self.contract_rate,
            'contract_rate': self.contract_rate,
        }
        apply = self.env['loan.apply'].sudo().with_context(
            {'mail_create_nosubscribe': True, }).create(val)
        if self.saler_id:
            apply.message_subscribe_users(user_ids=[self.saler_id.id])
        return apply

    bigdata_credit_count = fields.Integer(u"大数据征信", compute='_compute_bigdata_credit_count')

    # bigdata_ids = fields.One2many('loan.bigdata', 'loan_id', string=u"大数据征信信息")

    @api.multi
    def _compute_bigdata_credit_count(self):
        for loan in self:
            loan.bigdata_credit_count = self.env['loan.bigdata'].search_count(
                [('borrower_id', '=', loan.borrower_id.id)])

    def action_bigdata_credit(self):
        report_id = self.action_tongdun_apply()['report_id']
        # print report_id
        # report_id = u'ER20180531105555C2D1AD15'
        self.action_tongdun_query(report_id)
        # for credit in self:
        #     credit.loan_count = self.env['loan.loan'].search_count(
        #         [('credit_id', '=', credit.id)])
        # tongdong=TongDun.TongDun()

    def action_tongdun_apply(self):
        pr_data = {
            'name': u'皮晴晴',
            'id_number': '520001190812121210',
            'mobile': '13100000000'
        }
        pr_data1 = {
            'name': self.borrower_id.name,
            'id_number': self.borrower_id.identity,
            'mobile': self.borrower_id.phone
        }
        print pr_data1
        report = tongdun.pre_loan_apply(pr_data1)
        # print report
        # report = 1
        return report

    def action_tongdun_query(self, report_id):
        # report_id = 'ER2018051821064167CDCB5B'
        print report_id
        ret = tongdun.pre_loan_report(report_id)
        if ret.get('success'):
            self.action_create_record(ret)
        else:
            mes = "调用失败，错误码: {0}, 原因:{1} ".format(ret['reason_code'], ret['reason_desc'])
            print mes

    def action_create_record(self, ret):
        lists = []
        if ret.has_key('risk_items'):
            # 循环检测项
            for item in ret['risk_items']:
                detail = ''
                # 如果有详情数据
                if item.has_key('item_detail'):
                    item_detail = item['item_detail']

                    # namelist_hit_details数据 （风险信息扫描，个人基本信息核查）
                    if item_detail.has_key('namelist_hit_details'):
                        namelist_hit_details = item_detail['namelist_hit_details'][0]

                        # 法院的详情
                        if namelist_hit_details.has_key('court_details'):
                            for x in namelist_hit_details['court_details']:
                                if x['fraud_type'] != u"法院执行":
                                    detail += u"{}，{}，{}岁，所在省份：{}，生效法律文书确定的义务：{}  \n失信被执行人行为具体情形：{}，执行依据文号：{} \n 执行法院:{}，立案时间：{}，案号：{}。\n\n".format(
                                        x['name'], x['gender'], x['age'], x['province'], x['duty'],
                                        x['discredit_detail'],
                                        x['execution_base'], x['court_name'], x['filing_time'], x['case_number'])
                                else:
                                    str = u" 风险类型：{},案号：{}，执行法院:{}，立案时间：{}"
                                    detail += str.format(x['fraud_type'], x['case_number'], x['court_name'],
                                                         x['filing_time'])
                        else:
                            detail += u"风险类型：{}，匹配字段：{} ".format(namelist_hit_details['fraud_type'],
                                                                 namelist_hit_details['hit_type_displayname'])

                    # 风险信息的逾期信息
                    elif item_detail.has_key('overdue_details'):
                        overdue_details = item_detail['overdue_details'][0]
                        detail += u"逾期次数：{},逾期金额：{}，逾期笔数：{}，逾期天数：{}，逾期入库时间：{}。  ".format(item_detail['discredit_times'],
                                                                                         overdue_details[
                                                                                             'overdue_amount_range'],
                                                                                         overdue_details[
                                                                                             'overdue_count'],
                                                                                         overdue_details[
                                                                                             'overdue_day_range'],
                                                                                         overdue_details[
                                                                                             'overdue_time'])
                    # 客户行为检测
                    elif item_detail.has_key('frequency_detail_list'):
                        detail += u"客户行为检测： \n"
                        for frequency in item_detail['frequency_detail_list']:
                            detail += u'''{}。   \n'''.format(frequency['detail'])
                            if frequency.has_key('data'):
                                data = u'，  '.join(frequency['data'])
                                detail += u"证件号：{}。   \n".format(data)

                    # 多平台借贷申请，负债检测
                    elif item_detail.has_key('platform_detail'):
                        data = u'， '.join(item_detail['platform_detail'])
                        detail += u"总个数：{}\n{}  \n".format(item_detail['platform_count'], data)
                        if item_detail.has_key('platform_detail_dimension'):
                            detail += u'''各维度多头详情:   \n'''
                            for dimension in item_detail['platform_detail_dimension']:
                                more_detail = u'，'.join(dimension['detail'])
                                detail += u'''{}，{}，{}。   \n'''.format(dimension['dimension'], dimension['count'],
                                                                       more_detail)

                # 基本数据
                level = u''
                if item['risk_level'] == 'high':
                    level = u'高'
                elif item['risk_level'] == 'medium':
                    level = u'中'
                elif item['risk_level'] == 'low':
                    level = u'低'
                group_vals = {
                    'group_type': item['group'],
                    'item_name': item['item_name'],
                    'risk_level': level,
                    'item_detail': detail
                }
                # t = (0, 0, group_vals)
                lists.append((0, 0, group_vals))
                # print detail+'\n'

        # print len(lists)
        timeStamp = ret['report_time']
        timeStamp /= 1000.0
        timearr = time.localtime(timeStamp)
        otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timearr)
        vals = {
            'borrower_id': self.credit_id.borrower_id.id,
            'name': self.credit_id.borrower_id.name,
            'identity': self.credit_id.borrower_id.identity,
            'mobile': self.credit_id.borrower_id.phone,
            'report_id': ret['report_id'],
            'report_time': otherStyleTime,
            'final_score': ret['final_score'],
            'final_decision': ret['final_decision'],
            # 'child_ids': lists
            'riskitems_ids': lists
        }
        record = self.env['loan.bigdata'].sudo().create(vals)
        # self.bigdata_ids += record

    apply_count = fields.Integer(u"请款数", compute='_compute_apply_count')

    @api.multi
    def _compute_apply_count(self):
        for loan in self:
            loan.apply_count = self.env['loan.apply'].with_context(active_test=False).sudo().search_count(
                [('loan_id', '=', loan.id)])

    @api.multi
    def _track_subtype(self, init_values):
        self.ensure_one()
        old_partner_ids = self.message_partner_ids.mapped('id')
        self.message_subscribe(partner_ids=old_partner_ids, subtype_ids=[self.env.ref('mail.mt_comment').id, ],
                               force=True)
        if 'state' in init_values and self.state == 'homing':
            jfzg = self.env.ref('loan.group_loan_jfzg')
            jfzg_ids = jfzg.users.mapped('partner_id.id')
            # self.message_unsubscribe_users(user_ids=zhlr_ids, subtype_ids=[self.env.ref('loan.mt_loan_todo').id, ])
            self.message_subscribe(partner_ids=jfzg_ids, subtype_ids=[self.env.ref('loan.mt_loan_todo').id, ],
                                   force=True)
            return 'loan.mt_loan_todo'
            # return 'mail.mt_comment'
        elif 'state' in init_values and self.state == 'phoning':
            dszg = self.env.ref('loan.group_loan_dszg')
            dszg_ids = dszg.users.mapped('partner_id.id')
            # self.message_unsubscribe_users(user_ids=zhlr_ids, subtype_ids=[self.env.ref('loan.mt_loan_todo').id, ])
            self.message_subscribe(partner_ids=dszg_ids, subtype_ids=[self.env.ref('loan.mt_loan_todo').id, ],
                                   force=True)
            return 'loan.mt_loan_todo'
        elif 'state' in init_values and self.state == 'auditing':
            fkzj = self.env.ref('loan.group_loan_fkzj')
            fkzj_ids = fkzj.users.mapped('partner_id.id')
            # self.message_unsubscribe_users(user_ids=zhlr_ids, subtype_ids=[self.env.ref('loan.mt_loan_todo').id, ])
            self.message_subscribe(partner_ids=fkzj_ids, subtype_ids=[self.env.ref('loan.mt_loan_todo').id, ],
                                   force=True)
            return 'loan.mt_loan_todo'
        elif 'phoning_id' in init_values and self.state == 'phoning' and self.phoning_id:
            self.message_subscribe(partner_ids=[self.phoning_id.partner_id.id, ],
                                   subtype_ids=[self.env.ref('loan.mt_loan_todo').id, ],
                                   force=True)
            return 'loan.mt_loan_todo'
        # return 'mail.mt_note'
        return super(Loan, self)._track_subtype(init_values)
