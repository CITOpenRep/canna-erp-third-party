# Copyright (C) 2020-TODAY Serpent Consulting Services Pvt. Ltd. (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ExtendedApprovalWorkflowMixin(models.AbstractModel):
    _name = "extended.approval.workflow.mixin"
    _inherit = "extended.approval.mixin"

    def abort_approval(self):
        super(ExtendedApprovalWorkflowMixin, self).abort_approval()
        self.write({"state": self.workflow_start_state})
        return {}
