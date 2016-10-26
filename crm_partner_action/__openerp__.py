# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) 2015 Onestein BV (www.onestein.eu).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'CRM Partner Action',
    'version': '8.0.1.1.1',
    'website' : 'https://www.onestein.eu',
    'license': 'AGPL-3',
    'category': 'CRM',
    'summary': 'Register Action to do for partners',
    'author': 'Onestein BV, André Schenkels',
    'depends': [
        'base',
        'mail',
        'crm_visit',
        'sale',
    ],
    'data': [
        'security/crm_partner_action_security.xml',
        'security/ir.model.access.csv',
        'views/menu_item.xml',
        'views/mail_message_subtype.xml',
        'views/crm_partner_action_group.xml',
        'views/crm_partner_action.xml',
        'views/res_partner.xml',
        'data/crm_partner_action_sequence.xml'
    ],

}
