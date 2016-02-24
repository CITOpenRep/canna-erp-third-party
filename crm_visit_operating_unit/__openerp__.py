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
    "name": "Operating Unit in CRM Visit",
    "version": "8.0.1.0.0",
    "summary": "An operating unit (OU) is an organizational entity part of a "
               "company",
    "author": "Onestein BV, André Schenkels"
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "http://www.onestein.eu",
    "category": "CRM",
    "depends": ["crm_visit", "operating_unit"],
    "data": [
        "views/crm_visit.xml",
        "views/crm_visit_feeling.xml",
        "views/crm_visit_reason.xml",
        "security/crm_visit_security.xml",
        "security/crm_visit_feeling_security.xml",
        "security/crm_visit_reason_security.xml",
    ],
}
