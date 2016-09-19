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

from openerp import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    actions = fields.One2many(
        comodel_name='crm.partner.action',
        inverse_name='partner_id',
        string='Actions'
    )

    partner_action_count = fields.Integer(
        string='Number of actions',
        compute='_get_partner_action_count',
    )

    @api.one
    @api.depends('actions')
    def _get_partner_action_count(self):
        action_count = len(self.actions) or 0
        child_count = 0
        for child in self.child_ids:
            child_count += len(child.actions) or 0
        parent_count = len(self.parent_id.actions) or 0
        self.partner_action_count = action_count + child_count + parent_count
