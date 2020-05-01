# -*- coding: utf-8 -*-
from openerp import models


class PurchaseOrder(models.Model):
    _name = 'purchase.order'
    _inherit = ['purchase.order', 'extended.approval.workflow.mixin']

    workflow_signal = 'purchase_approve'
