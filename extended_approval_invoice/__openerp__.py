# -*- coding: utf-8 -*-

{
    'name': 'Extended Approval Invoice',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Onestein',
    'category': 'base',
    'depends': [
        'account',
        'base_extended_approval',
    ],
    'data': [
        'views/account_invoice.xml',
    ],
    'installable': True,
}
