# -*- coding: utf-8 -*-
from openerp import api, models


class ExtendedApprovalFlow(models.Model):
    _inherit = 'extended.approval.flow'

    @api.model
    def _get_extended_approval_models(self):
        return super(
            ExtendedApprovalFlow,
            self)._get_extended_approval_models() + [
                ('purchase.order', 'Purchase')
            ]
