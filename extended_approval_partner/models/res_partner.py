# Copyright (C) 2020-TODAY Serpent Consulting Services Pvt. Ltd. (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = ["res.partner", "extended.approval.mixin"]

    workflow_state_field = "state"
    workflow_state = "extended_approval"
    workflow_start_state = "draft"

    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("extended_approval", "Approval"),
            ("confirmed", "Confirmed"),
        ],
        default="draft",
        string="State",
    )

    def set_state_to_confirmed(self):
        self.approve_step()
        self.state = "confirmed"

    def reset_to_draft(self):
        self.cancel_approval()
        self.state = "draft"
