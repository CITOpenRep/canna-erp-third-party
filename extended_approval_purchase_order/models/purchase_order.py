# Copyright (C) 2020-TODAY Serpent Consulting Services Pvt. Ltd. (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _name = "purchase.order"
    _inherit = ["purchase.order", "extended.approval.workflow.mixin"]

    workflow_start_state = "draft"

    state = fields.Selection(
        selection_add=[("extended_approval", "Approval")],
        string="Status",
        readonly=True,
        index=True,
        copy=False,
        default="draft",
        tracking=True,
    )

    def action_cancel(self):
        self.cancel_approval()
        return super(PurchaseOrder, self).action_cancel()

    def write(self, values):
        result = self.approve_step()
        if not result:
            return super(PurchaseOrder, self).write(values)
        if values.get("state", False) == "purchase":
            values["state"] = "extended_approval"
        return super(PurchaseOrder, self).write(values)
