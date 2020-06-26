# Copyright (C) Onestein 2019-2020
# Copyright (C) Noviat 2020
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class PurchaseOrder(models.Model):
    """
    PO state selection:
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    """

    _name = "purchase.order"
    _inherit = ["purchase.order", "extended.approval.workflow.mixin"]

    workflow_signal = "purchase"
    workflow_start_state = "draft"

    def action_cancel(self):
        self.cancel_approval()
        return super().action_cancel()
