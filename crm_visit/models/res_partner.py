# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
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

from openerp import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    visit_ids = fields.One2many(
        comodel_name='crm.visit',
        inverse_name='partner_id',
        string='Visits')
    visits_count = fields.Integer(
        string='Number of visits',
        compute='_get_visits_count')

    @api.one
    @api.depends('visit_ids')
    def _get_visits_count(self):
        visit_count = len(self.visit_ids) or 0
        child_count = 0
        for child in self.child_ids:
            child_count += len(child.visit_ids)
        parent_count = len(self.parent_id.visit_ids) or 0
        self.visits_count = visit_count + child_count + parent_count
