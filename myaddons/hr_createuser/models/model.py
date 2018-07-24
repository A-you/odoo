# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError, Warning


class EmpCreateUser(models.Model):
    _inherit ="hr.employee"

    # user_id = fields.Many2one('res.user',string='调试人')
    UserJop = []
    def create_user_kfjl(self):
	    UserJop = '客户经理'
	    self.create_user_staff(UserJop)

    def create_user_zhlr(self):
		UserJop = '驻行录入'
		self.create_user_staff(UserJop)

    def create_user_zhzg(self):
	    UserJop = '驻行主管'
	    self.create_user_staff(UserJop)

    def create_user_jfzy(self):
	    UserJop = '家访专员'
	    self.create_user_staff(UserJop)

    def create_user_jfzg(self):
	    UserJop = '家访主管'
	    self.create_user_staff(UserJop)

    def create_user_dszy(self):
	    UserJop = '电审专员'
	    self.create_user_staff(UserJop)

    def create_user_dszg(self):
	    UserJop = '电审主管'
	    self.create_user_staff(UserJop)

    def create_user_zly(self):
	    UserJop = '资料员'
	    self.create_user_staff(UserJop)

    def create_user_fkzj(self):
	    UserJop = '风控总监'
	    self.create_user_staff(UserJop)

    # @api.multi
    def create_user_staff(self,UserJop):
	    user_password = self.mobile_phone[-4:]
	    if self.env['res.users'].sudo().search([('login', '=', self.mobile_phone)]):
		    return self.env.user.notify_warning(u'添加失败，该登录用户名已存在，不能再添加')
	    else:
		    if self.env['res.users'].search([('name', '=', UserJop)]):
			    UserSet = self.env['res.users'].search([('name', '=', UserJop)]).copy_data()
			    for key in UserSet:
				    UserPower = key['groups_id']
			    val = {
				    'name': self.name_related,
				    'login': self.mobile_phone,
				    'password': user_password,
				    # 下面可选择复制客户经理权限kfjler
				    'groups_id': UserPower,
			    }
			    self.env['res.users'].sudo().create(val)
			    return self.env.user.notify_info(u'添加成功')
		    else:
			    return self.env.user.notify_warning('用户中不存在%s ，请联系系统管理员添加' % (UserJop))
			    # return self.env.user.notify_warning('用户中不存在 % s  ，请联系系统管理员添加' % (self.UserJop))

    # @api.multi
    # def create_user_zhzg(self):
	 #    user_password = self.mobile_phone[-4:]
	 #    if self.env['res.users'].sudo().search([('login', '=', self.mobile_phone)]):
		#     return self.env.user.notify_warning(u'添加失败，该登录用户名已存在，不能再添加')
	 #    else:
		#     if self.env['res.users'].search([('name', '=', '驻行主管')]):
		# 	    kfjl = self.env['res.users'].search([('name', '=', '驻行主管')]).copy_data()
		# 	    for key in kfjl:
		# 		    kfjler = key['groups_id']
		# 	    val = {
		# 		    'name': self.name_related,
		# 		    'login': self.mobile_phone,
		# 		    'password': user_password,
		# 		    # 下面可选择复制客户经理权限kfjler
		# 		    'groups_id': kfjler
		# 	    }
		# 	    self.env['res.users'].sudo().create(val)
		# 	    return self.env.user.notify_info(u'添加成功')
		#     else:
		# 	    return self.env.user.notify_warning(u'用户中不存在客服经理，请联系系统管理员添加')




    # @api.multi
    # def create_user_staff(self):
	 #    # print type(self.mobile_phone)
	 #    # print self
	 #    # 截取电话号码后四位作为登录密码
	 #    user_password = self.mobile_phone[-4:]
	 #    if self.env['res.users'].sudo().search([('login','=',self.mobile_phone)]):
		#     return self.env.user.notify_warning(u'添加失败，该登录用户名已存在，不能再添加')
	 #    else:
		#     # kflj = self.env['res.users'].sudo().search([('name','=','尤名宇')]).copy()
    #
		#     #
		#     # print kflj
		#     # 用户中必须要有名字为客户经理这个用户
		#     kfjl = self.env['res.users'].search([('name', '=', '客户经理')]).copy_data()
		#     # print kfjl
		#     # kfjler = []
		#     for key in kfjl:
		# 	    # print key
		# 	    # print key['groups_id'],type(key['groups_id'])
		# 	    # 创建一个客户经理所有权限的，包括除了车贷系统外的权限
		# 	    kfjler = key['groups_id']
		# 	    # return kfjler
		# 	    # for i in key:
		# 	    #     print i
		#     # print kfjl.groups_id
		#     # print kfjler
		#     zhzger = self.env['res.users'].search([('name','=','驻行主管')]).copy_data()
		#     # print zhzger
		#     for key in zhzger:
		# 	    # 创建一个驻行主管的权限，包括车贷系统外的其他权限。
		# 	    zhzgk = key['groups_id']
		#     # print zhzgk
		#     # 下面是直接去查询权限组的数据，复制过来赋值好像出问题，它会把车贷系统外的权限默认。
		#     # zhzg = self.env['res.groups'].search([('name','=','驻行主管')]).copy_data()
		#     # print  zhzg
	 #    # print user_password
		#     val = {
		# 	    'name':self.name_related,
		# 	    'login': self.mobile_phone,
		# 	    'password':user_password,
		# 	    # 下面可选择复制客户经理权限kfjler
		# 	    'groups_id':zhzgk
		#     }
		#     # print val
		#     # print  type(val)
		#     self.env['res.users'].sudo().create(val)
	 #    return  self.env.user.notify_info(u'添加成功')