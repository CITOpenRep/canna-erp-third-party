# -*- coding: utf-8 -*-

{
    'name': 'Extended Approval Partners',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Onestein',
    'category': 'base',
    'depends': [
        'base',
        'base_extended_approval',
    ],
    'data': [
        'data/ir_filters_data.xml',
        'data/email_template_data.xml',
        'data/ir_actions_server_data.xml',
        'data/base_action_rule_data.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
}
