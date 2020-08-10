# Copyright (c) 2015 Onestein BV (www.onestein.eu).
# Copyright (C) 2020-TODAY SerpentCS Pvt. Ltd. (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    actions = fields.One2many(
        comodel_name="crm.partner.action", inverse_name="partner_id", string="Actions"
    )

    partner_action_count = fields.Integer(
        string="Number of actions", compute="_compute_get_partner_action_count"
    )

    def _compute_get_partner_action_count(self):
        action_count = len(self.actions) or 0
        child_count = 0
        for child in self.child_ids:
            child_count += len(child.actions) or 0
        parent_count = len(self.parent_id.actions) or 0
        self.partner_action_count = action_count + child_count + parent_count
