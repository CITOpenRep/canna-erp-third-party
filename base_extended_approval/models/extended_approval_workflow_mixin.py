# Copyright (C) Onestein 2019-2020
# Copyright (C) Noviat 2020
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class ExtendedApprovalWorkflowMixin(models.AbstractModel):
    """
    The Odoo workflow mechanism is replaced by an interception of the write method
    in the object where the workflow_state_field change
    """

    _name = "extended.approval.workflow.mixin"
    _inherit = "extended.approval.mixin"

    workflow_signal = "undefined"
    workflow_state_field = "state"
    workflow_state = "extended_approval"
    workflow_start_state = "draft"
    workflow_idx_state = "draft"

    @api.model
    def _setup_complete(self):
        """Add extra workflow state to the workflow_state_field """
        super()._setup_complete()
        field = self.fields_get().get(self.workflow_state_field)
        if field:
            try:
                state_names = [t[0] for t in field["selection"]]
                if self.workflow_state not in state_names:
                    if self.workflow_start_state in state_names:
                        field["selection"].insert(
                            max(state_names.index(self.workflow_idx_state) - 1, 0),
                            (self.workflow_state, "Approval"),
                        )
                    else:
                        field["selection"].append((self.workflow_state, "Approval"))
            except TypeError:
                # probably a callable selection attribute
                # TODO: decorated callable
                pass

    def abort_approval(self):
        super().abort_approval()
        self.write({self.workflow_state_field: self.workflow_start_state})
        return {}

    def write(self, vals):
        super().write(vals)
        for rec in self:
            if rec.workflow_state_field in vals:
                wstate = vals.get(rec.workflow_state_field)
                if wstate == rec.workflow_signal:
                    rec.approve_step()
                    if rec.current_step:
                        setattr(rec, rec.workflow_state_field, rec.workflow_state)
