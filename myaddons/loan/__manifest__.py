# -*- coding: utf-8 -*-
{
    'name': 'Credit Card Installment',
    'version': '1.0',
    'author': 'Ryan',
    'maintainer': 'Ryan',
    'website': 'http://www.cxyjf.cn',
    'license': 'LGPL-3',
    'category': 'Loans',
    'sequence': 1,
    'summary': '金融服务',
    'depends': [
        'base', 'mail',
        'field_image_preview',
        'web_notify', 'web_readonly_bypass',
        'china_city', 'dingtalk', 'oejia_wx'
    ],
    'external_dependencies': {
        'python': [
            'transitions',
        ],
    },
    'data': [
        'security/loan_security.xml',
        'security/ir.model.access.csv',
        'data/ir_cron.xml',

        'views/loan_bigdata_view.xml',

        'views/loan_menu.xml',
        'views/loan_menu_other.xml',

        'views/loan_borrower_view.xml',
        'views/loan_credit_view.xml',
        'views/loan_view.xml',
        'views/loan_apply_view.xml',
        'views/loan_graph.xml',

        'views/res_config_views.xml',
        'data/loan_sequence_data.xml',
        'data/loan_data.xml',

    ],
    'installable': True,
    'application': True,
}
