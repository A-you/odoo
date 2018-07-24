# -*- coding: utf-8 -*-

from odoo import api, fields, models
import xlrd
import base64


class LoanConfiguration(models.TransientModel):
    _name = 'loan.config.settings'
    _inherit = 'res.config.settings'

    yt_appid = fields.Char('AppId',
                           default=lambda self: self.env['ir.values'].sudo().get_default('loan.config.settings',
                                                                                         'yt_appid') or '10124678')
    yt_secret_id = fields.Char('AppSecret',
                               default=lambda self: self.env['ir.values'].sudo().get_default('loan.config.settings',
                                                                                             'yt_secret_id') or 'AKID1whKl2PCLOGxSmrtfQDtRp253saMpXrz')
    yt_secret_key = fields.Char('AppSecretKey',
                                default=lambda self: self.env['ir.values'].sudo().get_default('loan.config.settings',
                                                                                              'yt_secret_key') or '7d5NYdXIsHVXSHzWv9Fh0BD3jFYklbGj')
    yt_userid = fields.Char('UserId',
                            default=lambda self: self.env['ir.values'].sudo().get_default('loan.config.settings',
                                                                                          'yt_userid') or '1227400499')
    yt_end_point = fields.Char('EndPoint',
                               default=lambda self: self.env['ir.values'].sudo().get_default('loan.config.settings',
                                                                                             'EndPoint') or 'TencentYoutuyun.conf.API_YOUTU_END_POINT')
    yt_session_id = fields.Char('SessionId', default='')

    @api.multi
    def set_default_yt_appid(self):
        check = self.env.user.has_group('base.group_system')
        Values = check and self.env['ir.values'].sudo() or self.env['ir.values']
        for config in self:
            Values.set_default('loan.config.settings', 'yt_appid', config.yt_appid)

    @api.multi
    def set_default_yt_secret_id(self):
        check = self.env.user.has_group('base.group_system')
        Values = check and self.env['ir.values'].sudo() or self.env['ir.values']
        for config in self:
            Values.set_default('loan.config.settings', 'yt_secret_id', config.yt_secret_id)

    @api.multi
    def set_default_yt_secret_key(self):
        check = self.env.user.has_group('base.group_system')
        Values = check and self.env['ir.values'].sudo() or self.env['ir.values']
        for config in self:
            Values.set_default('loan.config.settings', 'yt_secret_key', config.yt_secret_key)

    @api.multi
    def set_default_yt_userid(self):
        check = self.env.user.has_group('base.group_system')
        Values = check and self.env['ir.values'].sudo() or self.env['ir.values']
        for config in self:
            Values.set_default('loan.config.settings', 'yt_userid', config.yt_userid)

    @api.multi
    def set_default_yt_end_point(self):
        check = self.env.user.has_group('base.group_system')
        Values = check and self.env['ir.values'].sudo() or self.env['ir.values']
        for config in self:
            Values.set_default('loan.config.settings', 'yt_end_point', config.yt_end_point)

    xls = fields.Binary(u'表格文件')

    # rn:原有的独立model方法
    def btn_import(self, context=None):
        print(self.ids)
        for wiz in self.browse(self.ids):
            # print(wiz.xls)
            if not wiz.xls:
                continue
            excel = xlrd.open_workbook(file_contents=base64.decodestring(wiz.xls))
            sheets = excel.sheets()
            # print(sheets)
            for sh in sheets:
                for row in range(1, sh.nrows):
                    line = sh.cell(row, 0).value
                    firm = sh.cell(row, 1).value
                    name = sh.cell(row, 3).value
                    # jp = sh.cell(row, 3).value

                    # read state
                    firms = self.env['loan.car.firm'].search([('name', '=', firm)])
                    if len(firms):
                        lines = self.env['loan.car.line'].search([('name', '=', line)])
                        if len(lines):
                            names = self.env['loan.car.name'].search([('name', '=', name)])
                            if len(names):
                                continue
                            else:
                                self.env['loan.car.name'].create({'name': name, 'line': lines[0].id})
                        else:
                            line_id = self.env['loan.car.line'].create({'name': line, 'firm': firms[0].id})

                            self.env['loan.car.name'].create({'name': name, 'line': line_id.id})
                    else:
                        firm_id = self.env['loan.car.firm'].create({'name': firm, })
                        line_id = self.env['loan.car.line'].create({'name': line, 'firm': firm_id.id})
                        self.env['loan.car.name'].create({'name': name, 'line': line_id.id})
            # TODO 考虑增加对文件格式的容错操作，并提示完成

    # rn:考虑整合到销售产品模块
    def btn_import_product(self, context=None):
        print(self.ids)
        for wiz in self.browse(self.ids):
            # print(wiz.xls)
            if not wiz.xls:
                continue
            excel = xlrd.open_workbook(file_contents=base64.decodestring(wiz.xls))
            sheets = excel.sheets()
            # print(sheets)
            for sh in sheets:
                for row in range(2, sh.nrows):
                    print row
                    line = sh.cell(row, 0).value
                    name = sh.cell(row, 3).value
                    car_name = line + ' ' + name
                    description_purchase = sh.cell(row, 19).value
                    categ_id = 4

                    # firms = self.env['product.template'].search([('name', '=', car_name)])
                    if self.env['product.template'].search_count([('name', '=', car_name)]) == 0:
                        print car_name
                        self.env['product.template'].create(
                            {'name': car_name,
                             'description_purchase': description_purchase,
                             'categ_id': categ_id
                             })
