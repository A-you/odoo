# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class BigData(models.Model):
    _name = "loan.bigdata"
    _description = u"征信大数据"

    active = fields.Boolean(default=True)

    borrower_id = fields.Many2one('loan.borrower', string=u"客户id")
    riskitems_ids = fields.One2many('loan.riskitem', 'bigdata_id', string=u"风险项ids")
    #  报告参数
    report_id = fields.Char(u"报告编号")
    report_time = fields.Date(u"报告时间")
    final_decision = fields.Char(u"风险结果")
    final_score = fields.Integer(u"风险分数")
    # apply_time = fields.Date(u"扫描时间")
    # application_id = fields.Date(u"申请编号")

    # 基本数据
    name = fields.Char(u"姓名")
    sex = fields.Char(u"性别")
    mobile = fields.Char(u"手机号码")
    identity = fields.Char(u"证件号码")
    age = fields.Char(u"年龄")
    marriage = fields.Char(u"婚姻状况")
    edu = fields.Char(u"学历")
    homeAddress = fields.Char(u"家庭地址")
    company = fields.Char(u"公司名称")

    # 还款能力

    # 归属地
    id_card_address = fields.Char(u"身份证归属地")
    true_ip_address = fields.Char(u"IP归属地")
    wifi_address = fields.Char(u"WIFI归属地")
    cell_address = fields.Char(u"基站归属地")
    bank_card_address = fields.Char(u"银行卡归属地")
    mobile_address = fields.Char(u"手机归属地")

    # 	个人基本信息核实
    name_identity_matched = fields.Boolean(u"姓名身份证匹配")
    face_matched = fields.Boolean(u"人脸识别")
    address_matched = fields.Boolean(u"地址核查")
    company_matched = fields.Boolean(u"公司核查")
    mobile_status = fields.Char(u"手机号状态")
    mobile_online_time = fields.Char(u"公司核查")


# 公检法 风险信息扫描

# isIn_lose_credit_record = fields.Boolean(u"身份证是否命中法院失信名单")
# isIn_lawsuit_record = fields.Boolean(u"身份证是否命中法院结案名单")
# isIn_execute_record = fields.Boolean(u"身份证是否命中法院执行名单")
#
# isIn_black_record = fields.Boolean(u"身份证是否命中法院黑名单")
# isIn_debt_record = fields.Boolean(u"身份证是否命中欠款公司法人代表名单")
# isIn_high_risk_record =fields.Boolean(u"手机号码是否命中高风险关注名单")
# discredit_count = fields.Boolean(u"身份证是否命中信贷逾期名单")
#
# lose_credit_info = fields.Text(u"失信记录信息")
# lawsuit_record_info =fields.Text(u"结案记录信息")
# execute_record_info =fields.Text(u"法院执行记录信息")
# black_record_info =  fields.Text(u"黑名单记录信息")

class RiskItem(models.Model):
    _name = 'loan.riskitem'
    _description = u"大数据风险项"
    _rec_name = 'item_name'

    bigdata_id = fields.Many2one('loan.bigdata', string=u"大数据征信单号", ondelete='cascade')

    report_id = fields.Char(u"报告编号")
    group_type = fields.Char(u"风险类型")
    item_name = fields.Char(u"风险项名称")
    risk_level = fields.Char(u"风险等级")
    item_detail = fields.Text(u"风险检测详情")
