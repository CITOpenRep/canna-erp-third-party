# Copyright (C) 2020-TODAY SerpentCS Pvt. Ltd. (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountInvoice(models.Model):
    _name = "account.move"
    _inherit = ["account.move", "extended.approval.workflow.mixin"]

    state = fields.Selection(
        selection_add=[("extended_approval", "Approval")],
        string="Status",
        required=True,
        readonly=True,
        copy=False,
        tracking=True,
        default="draft",
    )

    def action_cancel(self):
        self.cancel_approval()
        return super(AccountInvoice, self).action_cancel()

    def write(self, values):
        result = self.approve_step()
        if not result:
            return super(AccountInvoice, self).write(values)
        if self.current_step:
            values["state"] = "extended_approval"
        return super(AccountInvoice, self).write(values)
