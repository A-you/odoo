# -*- coding: utf-8 -*-


from odoo import api, fields, tools, models, _

import tempfile
import TencentYoutuyun
import base64
import os
import re
from odoo.exceptions import ValidationError, Warning


class LoanBorrower(models.Model):
    _name = 'loan.borrower'
    _description = u'客户录入'
    _inherit = ['mail.thread']
    _inherits = {'res.partner': 'partner_id'}
    _order = 'order desc'
    _rec_name = 'name'

    _states = [
        ('draft', u'草稿'),
        ('confirmed', u'确认'),
    ]
    state = fields.Selection(
        _states, u'状态', default='draft', required=True, copy=False, index=True, readonly=True,
        track_visibility='onchange')

    partner_id = fields.Many2one('res.partner', required=True, ondelete='restrict', auto_join=True,
                                 string=u'关联伙伴')
    saler_id = fields.Many2one('res.users', required=True, ondelete='restrict', auto_join=True,
                               string=u'客户经理', default=lambda self: self.env.user)
    active = fields.Boolean(default=True, track_visibility='onchange')
    order = fields.Char(u'编号', copy=False, readonly=True)
    name = fields.Char(u'客户姓名', related='partner_id.name', inherited=True, track_visibility='onchange')
    identity = fields.Char(u'身份证号码', required=True, track_visibility='onchange')
    address = fields.Char(u'家庭住址', required=True, track_visibility='onchange')
    phone = fields.Char(u'手机', required=True, track_visibility='onchange')

    frontimage = fields.Binary(u"身份证正面", attachment=True, required=True, )
    backimage = fields.Binary(u"身份证反面", attachment=True, required=True, )

    credit_count = fields.Integer(u"征信数", compute='_compute_credit_count')

    bigdata_ids = fields.One2many('loan.bigdata', 'borrower_id', string=u"大数据征信信息")

    @api.multi
    def _compute_credit_count(self):
        for borrower in self:
            borrower.credit_count = self.env['loan.credit'].with_context(active_test=False).sudo().search_count(
                [('borrower_id', '=', borrower.id)])

    information_attachment = fields.Many2many('ir.attachment', compute='_get_attachment_ids', string=u'附件', )

    _sql_constraints = [('identity_uniq', 'UNIQUE (identity)', u'身份证号已存在！')]

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
        self.youtu = TencentYoutuyun.YouTu(appid, secret_id, secret_key, userid, end_point)

    @api.onchange('frontimage')
    def _identify_ID(self):
        self.ensure_one()
        if not self.frontimage:
            return
        data = base64.decodestring(self.frontimage)
        fobj = tempfile.NamedTemporaryFile(delete=False)
        fname = fobj.name
        fobj.write(data)
        fobj.close()
        try:
            self.set_API()
            retidcardocr = self.youtu.idcardocr(fname, data_type=0, card_type=0)
            print retidcardocr
            self.name = retidcardocr["name"].encode('iso8859-1').decode('utf-8')
            self.address = retidcardocr["address"].encode('iso8859-1').decode('utf-8')
            self.identity = retidcardocr["id"]
            print self.name, self.identity
        except Exception:
            raise Warning(_(u'API配置错误，请联系管理员！！'))
        finally:
            # delete the file when done
            os.unlink(fname)

    def valid_phone(self, phone):
        if re.match('^(13[0-9]|14[5|7]|15[0|1|2|3|5|6|7|8|9]|18[0|1|2|3|5|6|7|8|9])\d{8}$', phone):
            return True
        return False

    @api.model
    def create(self, vals):
        if not self.valid_phone(vals.get('phone')):
            self.env.user.notify_warning(u'手机号码格式不正确！')
            # rn:需要返回一个record id,所以不中断退出
        if not vals.get('order'):
            vals['order'] = self.env['ir.sequence'].next_by_code('loan.borrower') or '/'
            print vals['order']
        vals['frontimage'] = tools.image_resize_image_big(vals.get('frontimage'))
        return super(LoanBorrower, self).create(vals)

    def _get_attachments(self, attachments):
        return ', '.join([k.name for k in attachments])

    @api.multi
    def write(self, vals):
        # if not vals['active']:
        #     return super(LoanBorrower, self).write(vals)
        if vals.get('phone'):
            if not self.valid_phone(vals.get('phone')):
                return self.env.user.notify_warning(u'手机号码格式不正确！')
        elif not self.valid_phone(self.phone):
            return self.env.user.notify_warning(u'手机号码格式不正确！')
        if vals.get('frontimage'):
            vals['frontimage'] = tools.image_resize_image_big(vals.get('frontimage'))
        return super(LoanBorrower, self).write(vals)
        # old_attachments = self._get_attachments(self.information_attachment)
        # super(LoanBorrower, self).write(vals)
        # new_attachments = self._get_attachments(self.information_attachment)
        # if old_attachments != new_attachments:
        #     self.message_post(body="<ul><li>附件：%s <b>&#8594;</b>%s </li></ul>" % (old_attachments, new_attachments))
        #     # self.message_post(body="<b>关系人：</b> %s &#8594; %s" % (old_assigned_users, new_assigned_users))
        # return True

    def action_create_credit(self):
        val = {
            'saler_id': self.saler_id.id,
            'state': 'entering',
            'borrower_id': self.id,
        }
        print val
        credit = self.env['loan.credit'].sudo().with_context({'mail_create_nosubscribe': True, }).create(val)
        if self.saler_id:
            credit.message_subscribe_users(user_ids=[self.saler_id.id])
        # channel_ids = self.env['mail.channel'].sudo().search([('name', '=', u'风控'), ])
        # for channel_id in channel_ids:
        #     credit.message_subscribe(channel_ids=[channel_id.id, ], subtype_ids=[self.env.ref('loan.mt_loan_todo').id, ])

        return credit

    @api.multi
    def action_confirm(self):
        if not self.valid_phone(self.phone):
            return self.env.user.notify_warning(u'手机号码格式不正确！')
        self.write({'state': 'confirmed'})
        self.action_create_credit()
        return

    @api.multi
    def action_draft(self):
        if self.env['loan.credit'].search([('borrower_id', '=', self.id), ('state', '=', 'approved')]):
            return self.env.user.notify_warning(u'有相关征信查询，不能重置！')
        return self.write({'state': 'draft'})

    def _get_attachment_ids(self):
        att_model = self.env['ir.attachment']  # 获取附件模型
        for obj in self:
            query = [('res_model', '=', self._name), ('res_id', '=', obj.id)]  # 根据res_model和res_id查询附件
            obj.information_attachment = att_model.search(query)  # 取得附件list

    # @api.multi
    # def _track_subtype(self, init_values):
    #     self.ensure_one()
    #     if 'state' in init_values and self.state == 'sale':
    #         return 'sale.mt_order_confirmed'
    #     elif 'state' in init_values and self.state == 'sent':
    #         return 'sale.mt_order_sent'
    #     return super(SaleOrder, self)._track_subtype(init_values)
