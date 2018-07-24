# -*- coding: utf-8 -*-
{
	'name': '信用卡分期基础数据',
    'version': '1.0',
    'author': 'Ryan',
    'maintainer': 'Ryan',
    'website': 'http://www.cxyjf.cn',
    'license': 'LGPL-3',
    'category': 'Loans',
    'sequence': 1,
    'summary': '金融服务',
	'depends': ['base','loan'],
	'data':[
		'security/loan_after_security.xml',
		'security/ir.model.access.csv',
		'views/loan_record_stage_view.xml',
		'views/loan_basis_view.xml',
		'data/loan_sequence_data.xml',
		'views/inherit_apply_from_view.xml',
		'views/inherit_credit_from_view.xml',
		'wizard/loan_record_finance_view.xml',
		'wizard/loan_record_original_view.xml',
		'wizard/loan_record_copies_view.xml',

	],
	'installable': True,
	'application':False,
}
