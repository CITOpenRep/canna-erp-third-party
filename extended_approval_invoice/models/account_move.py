# Copyright (C) 2020-TODAY SerpentCS Pvt. Ltd. (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountInvoice(models.Model):
    _name = "account.move"
    _inherit = ["account.move", "extended.approval.workflow.mixin"]

    workflow_signal = "posted"
    workflow_state = "extended_approval"

    def action_cancel(self):
        self.cancel_approval()
        return super(AccountInvoice, self).action_cancel()
