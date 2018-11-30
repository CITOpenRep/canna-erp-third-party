# -*- coding: utf-8 -*-

{
    'name': 'Base Extended Approval',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Onestein',
    'category': 'base',
    'depends': [
        'base',
        'account',  # necessary for menu placement
    ],
    'data': [
        'views/base_extended_approval.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
