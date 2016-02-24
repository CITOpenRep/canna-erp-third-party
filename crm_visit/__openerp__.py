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
    'name': 'CRM Visit',
    'version': '8.0.1.0.0',
    'website' : 'https://www.onestein.eu',
    'license': 'AGPL-3',
    'category': 'CRM',
    'summary': '',
    'description': """
CRM Visit
=========
- Manage Customer visits
- Report on Customer visits

""",
    'author': 'Onestein BV, André Schenkels',
    'depends': [
        'base',
        'mail'
    ],
    'data': [
        'security/crm_visit_security.xml',
        'security/ir.model.access.csv',
        'views/menu_item.xml',
        'views/mail_message_subtype.xml',
        'views/crm_visit_feeling.xml',
        'views/crm_visit_reason.xml',
        'views/crm_visit.xml',
        'views/res_partner.xml',
        'data/crm_visit_sequence.xml'
    ],

}
