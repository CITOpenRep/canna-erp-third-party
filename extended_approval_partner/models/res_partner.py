# Copyright (C) 2020-TODAY SerpentCS Pvt. Ltd. (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = ["res.partner", "extended.approval.workflow.mixin"]

    workflow_signal = "confirmed"
    workflow_state = "extended_approval"

    state = fields.Selection(
        selection=[("draft", "Draft"), ("confirmed", "Confirmed")],
        default="draft",
        string="State",
    )

    def set_state_to_confirmed(self):
        # self.approve_step()
        self.state = "confirmed"
        return

    def reset_to_draft(self):
        self.ea_cancel_approval()
        self.state = "draft"
        return
