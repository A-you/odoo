# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': '几米API调用',
    'category': 'Base',
    'website': 'https://www.tfsodoo.com',
    'version': '1.0',
    'description': """
        调用几米API获取接口返回值
        """,
    'author': 'tfs',
    'depends': ['base'],
    'installable': True,
    'data': [
        'views/tfs_api_info.xml',
        'views/tfs_api_info_templates.xml'
    ],
    'demo': [
    ],
    'qweb':['static/src/xml/*.xml'],
    'application': True,
}
