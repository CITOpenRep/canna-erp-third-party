# -*- coding: utf-8 -*-
# Copyright (C) 2015 ICTSTUDIO (<http://www.ictstudio.eu>).
# Copyright (C) 2016-2019 Noviat nv/sa (www.noviat.com).
# Copyright (C) 2016 Onestein (http://www.onestein.eu/).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': "Sale Discount Advanced",
    'author': "ICTSTUDIO,Noviat,Onestein",
    'website': "http://www.ictstudio.eu",
    'category': 'Sales',
    'version': '8.0.3.1.0',
    'license': 'AGPL-3',
    'depends': [
        'sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/mail_message_subtype.xml',
        'views/res_partner_views.xml',
        'views/sale_discount_views.xml',
        'views/sale_order_views.xml',
    ],
    'demo': [
        'demo/sale_discount.xml',
        'demo/sale_discount_rule.xml',
    ]
}
