# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) 2016 Onestein BV (www.onestein.eu).
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
    'name': 'CRM Visit Partner Action - Intermediate module',
    'version': '8.0.1.0.1',
    'website' : 'https://www.onestein.eu',
    'license': 'AGPL-3',
    'category': 'CRM',
    'summary': '',
    'description': """
CRM Visit Partner Actions
=========================
- Show and work with Partner Actions on Visits

""",
    'author': 'Onestein BV, André Schenkels',
    'depends': [
        'crm_visit',
        'crm_partner_action'
    ],
    'data': [
        'views/crm_visit.xml',
    ],

}
