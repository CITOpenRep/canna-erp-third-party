# -*- coding: utf-8 -*-
# Copyright 2019 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Sale Order Group',
    'version': '8.0.1.1.0',
    'license': 'AGPL-3',
    'author': 'Noviat',
    'category': 'Sales',
    'depends': [
        'sale',
    ],
    'data': [
        'data/ir_sequence_data.xml',
        'security/sale_order_group_security.xml',
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'views/sale_order_group_views.xml',
        'wizards/sale_order_group_add_order.xml',
        'wizards/sale_order_group_create.xml',
    ],
    'installable': True,
}
