# -*- coding: utf-8 -*-
from openerp import api, models


class PurchaseOrder(models.Model):
    _name = 'purchase.order'
    _inherit = ['purchase.order', 'extended.approval.workflow.mixin']

    workflow_signal = 'purchase_approve'
    workflow_start_state = 'confirmed'

    @api.multi
    def action_cancel(self):
        self.cancel_approval()
        return super(PurchaseOrder, self).action_cancel()
