# -*- coding: utf-8 -*-
from openerp import models


class AccountInvoice(models.Model):
    _name = 'account.invoice'
    _inherit = ['account.invoice', 'extended.approval.workflow.mixin']

    workflow_signal = 'invoice_open'
    workflow_state = 'extended_approval'
