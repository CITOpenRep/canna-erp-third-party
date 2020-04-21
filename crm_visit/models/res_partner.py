# Copyright (c) 2015 Onestein BV (www.onestein.eu).
# Copyright (C) 2020-TODAY Serpent Consulting Services Pvt. Ltd. (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    visit_ids = fields.One2many(
        comodel_name="crm.visit", inverse_name="partner_id", string="Visits"
    )
    visits_count = fields.Integer(
        string="Number of visits", compute="_get_visits_count"
    )

    @api.depends("visit_ids")
    def _get_visits_count(self):
        visit_count = len(self.visit_ids) or 0
        child_count = 0
        for child in self.child_ids:
            child_count += len(child.visit_ids)
        parent_count = len(self.parent_id.visit_ids) or 0
        self.visits_count = visit_count + child_count + parent_count
