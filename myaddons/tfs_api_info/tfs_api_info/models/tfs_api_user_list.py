# -*- coding: utf-8 -*-
from odoo import models, fields, api
from ..controllers.main import tfs_api_info
import urllib, httplib, json
from odoo.exceptions import UserError


class tfsApiUserList(models.Model):
    _name = 'tfs.api.user.list'

    name = fields.Char(u'父账户名称', required=True)
    password = fields.Char(u'父账户密码', required=True)
    lines = fields.One2many('tfs.api.user.list.line', 'order_id', u'子账户')

    # 查询子账户方法
    @api.one
    def btn_search_list(self):
        app_key = '8FB345B8693CCD00D633786744140938'
        app_script = '2862ecf009f845d5bc76381c1eb5d849'
        server_url = 'open.aichezaixian.com'
        tfs_api_obj = tfs_api_info()
        # 获取通用参数
        parmse = tfs_api_obj.get_parmse('jimi.user.child.list', app_key)
        # 增加私有参数
        parmse['access_token'] = tfs_api_obj.get_token('jimi.oauth.token.get', app_key, app_script, self.name, self.password)  # access_token
        parmse['target'] = self.name  # 要查询的用户账号
        # 访问地址
        request_url = urllib.urlencode(parmse)
        httpsClient = httplib.HTTPConnection(server_url)
        httpsClient.request('POST', '/route/rest', request_url,
                            {"Content-type": "application/x-www-form-urlencoded"})
        ret_json = httpsClient.getresponse().read()
        ret_dict = json.loads(ret_json)
        # 判断返回值
        line_obj = self.env['tfs.api.user.list.line']
        if ret_dict.get('message') == 'success':
            list_all = []
            for line in ret_dict.get('result'):
                res_id = line_obj.create({
                    'name':line.get('name'),
                    'type':line.get('type'),
                    'displayflag':str(line.get('displayFlag','0')),
                    'address':line.get('address'),
                    'birth':line.get('birth'),
                    'companyname':line.get('companyName'),
                    'email':line.get('email'),
                    'phone':line.get('phone'),
                    'language':line.get('language'),
                    'sex':str(line.get('sex','0')),
                    'enabledflag':str(line.get('enabledFlag','0')),
                    'remark':line.get('remark'),
                })
                list_all.append(res_id.id)
            self.lines = [(6, 0, list_all)]
        else:
            if ret_dict.get('code') == 1004:
                raise UserError("access_token异常或请求频繁，请检查用户名和密码，并且1分钟以后再刷新！")
            else:
                raise UserError("%s"%ret_dict.get('message'))




class tfsApiUserListLine(models.Model):
    _name = 'tfs.api.user.list.line'

    order_id = fields.Many2one('tfs.api.user.list', u'父账户')
    name = fields.Char(u'账户名称')
    type = fields.Selection([(3, u'终端用户'), (8, u'一级代理商'), (9, u'普通用户'), (10, u'普通代理商'), (11, u'销售')], u'账户类型')
    displayflag = fields.Selection([('0', u'不启用'), ('1', u'启用')], u'是否启用')
    address = fields.Char(u'所在地')
    birth = fields.Char(u'生日')
    companyname = fields.Char(u'公司名')
    email = fields.Char(u'邮箱')
    phone = fields.Char(u'联系电话')
    language = fields.Char(u'语言')
    sex = fields.Selection([('0', u'男'), ('1', u'女')], u'性别')
    enabledflag = fields.Selection([('0', u'不可用'), ('1', u'可用')], u'性别',)
    remark = fields.Char(u'备注')
