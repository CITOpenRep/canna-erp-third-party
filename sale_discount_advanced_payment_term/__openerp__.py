# -*- coding: utf-8 -*-
# Copyright (C) 2016-2019 Noviat nv/sa (www.noviat.com).
# Copyright (C) 2016 Onestein (http://www.onestein.eu/).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Sale Discount on Payment Terms',
    'version': '8.0.1.2.0',
    'license': 'AGPL-3',
    'author': 'Noviat,Onestein',
    'website': 'http://www.noviat.com',
    'category': 'Sales',
    'depends': ['sale_discount_advanced'],
    'data': [
        'views/account_payment_term.xml',
        'views/sale_discount.xml',
        'views/sale_order.xml',
    ],
    'demo': [
        'demo/sale_discount_demo.xml'
    ],
    'installable': True,
}
