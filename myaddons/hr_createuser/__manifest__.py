# -*- coding: utf-8 -*-
{
    "name": "员工转为用户 employee users",
    "summary": 'The inheritance view and the inheritance module are modified',
    "version": "10.0.1.0.0",
    "website": "www.cxyjk.com",
    "author": "ymy",
    "license": "AGPL-3",
    'depends': ['hr','base','loan'],
    "application": True,
    'installable': True,
    "data": [
        # 'security/hr_security.xml',
        # 'security/ir.model.access.csv',

        'views/hr_createuser.xml',
        'views/scheduler_demo.xml',
        'views/filter_disable_view.xml',
    ],
}