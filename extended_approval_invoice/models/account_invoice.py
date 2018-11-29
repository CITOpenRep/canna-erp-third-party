# -*- coding: utf-8 -*-
from openerp import api, models


class AccountInvoice(models.Model):
    _name = 'account.invoice'
    _inherit = ['account.invoice', 'extended.approval.workflow.mixin']

    workflow_signal = 'invoice_open'
    workflow_state = 'extended_approval'

    @api.multi
    def action_cancel(self):
        self.cancel_approval()
        return super(AccountInvoice, self).action_cancel()
