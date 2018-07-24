# -*- coding: utf-8 -*-
from odoo import api, fields, tools, models, _
import json
import urllib2


def send_message(self, content):
    target_employee_ids = self.env['hr.employee'].search(
        [('mobile_phone', '=', self.saler_id.name), ('userid', '!=', False)])
    if not target_employee_ids:
        return False
    print target_employee_ids
    # 发送消息
    send_dingtalk_message(self, content, target_employee_ids[0].userid)


def send_dingtalk_message(self, content, role=None, old_homing_id=None):
    dingtalkAccount = self.env['dingtalk.account'].sudo().search([])
    if not dingtalkAccount:
        return False

    # 获得微应用
    dingtalkApp = self.env['dingtalk.app'].sudo().search([('send_enterprise_message', '=', True)])
    if not dingtalkApp:
        return False

    # target_employee_ids = self.env['hr.employee'].search(
    #     [('mobile_phone', '=', self.saler_id.login), ('userid', '!=', False)])

    target_employee_ids = []
    if role and role == 'jfzg':
        jfzg = self.env.ref('loan.group_loan_jfzg')
        if jfzg:
            # 这里只做的单个处理
            print jfzg.users[0].login
            target_employee_ids = self.env['hr.employee'].search(
                [('mobile_phone', '=', jfzg.users[0].login), ('userid', '!=', False)])

    elif role and role == 'jfzy':
        jfzy = ''
        if old_homing_id:
            jfzy = old_homing_id
        else:
            jfzy = self.homing_id
        if jfzy:
            print jfzy.name
            target_employee_ids = self.env['hr.employee'].search(
                [('mobile_phone', '=', jfzy.login), ('userid', '!=', False)])
    else:
        target_employee_ids = self.env['hr.employee'].search(
            [('mobile_phone', '=', self.saler_id.login), ('userid', '!=', False)])

    if not target_employee_ids:
        return False

    target_employee_id = target_employee_ids[0].userid

    message = {
        "touser": target_employee_id,
        "agentid": str(dingtalkApp[0].agent_id),
        "msgtype": "text",
        "text": {
            "content": content
        }
    }
    access_token = self.env['ir.values'].sudo().get_default('dingtalk.config.settings', 'dingtalk_accessToken')

    # url = "https://oapi.dingtalk.com/message/send?access_token={0}".format(access_token)
    url = "https://oapi.dingtalk.com/message/send?access_token={0}".format(dingtalkAccount[0].access_token)
    data = json.dumps(message, ensure_ascii=False).encode("utf-8")
    req = urllib2.Request(url, data)
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req).read()
    results = json.loads(response.decode("utf-8"))
    return results
