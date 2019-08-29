# -*- coding: utf-8 -*-
# Copyright 2019 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Sale Order Group Discount',
    'version': '8.0.1.0.0.',
    'license': 'AGPL-3',
    'author': 'Noviat',
    'category': 'Sales',
    'depends': [
        'sale_order_group',
        'sale_discount_advanced',
    ],
    'data': [
        'views/sale_order_group_views.xml',
    ],
    'installable': True,
}
