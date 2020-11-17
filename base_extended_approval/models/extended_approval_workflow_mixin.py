# Copyright (C) Onestein 2019-2020
# Copyright (C) Noviat 2020
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class ExtendedApprovalWorkflowMixin(models.AbstractModel):
    """
    The Odoo workflow mechanism is replaced by an interception of the write method
    in the object when the workflow_state_field change.
    """

    _name = "extended.approval.workflow.mixin"
    _inherit = "extended.approval.mixin"
    _description = "Mixin class for extended approval workflow"

    # signal to start the approval flow
    workflow_signal = "draft"
    # field used to track the approval flow. Must be a selection field
    workflow_state_field = "state"
    # value of the workflow_state_field for the approval
    workflow_state = "extended_approval"
    # fallback state when the approval is rejected
    workflow_start_state = "draft"

    @api.model
    def _setup_complete(self):
        """
        Insert extra  approval state in the workflow_state_field selection just before
        the workflow_signal or at the end if there is no workflow_signal is the
        selection
        """
        super()._setup_complete()
        field = self.fields_get().get(self.workflow_state_field)
        if field:
            try:
                state_names = [t[0] for t in field["selection"]]
                if self.workflow_state not in state_names:
                    if self.workflow_start_state in state_names:
                        field["selection"].insert(
                            state_names.index(self.workflow_signal),
                            (self.workflow_state, "Approval"),
                        )
                    else:
                        field["selection"].append((self.workflow_state, "Approval"))
            except TypeError:
                # probably a callable selection attribute
                # TODO: decorated callable
                pass

    def ea_abort_approval(self):
        super().ea_abort_approval()
        self.write({self.workflow_state_field: self.workflow_start_state})
        return {}

    def write(self, vals):
        """
        The super is made after the approval process in order to have a
        clean mailthread trying to limit the conversion of multi write to multiple
        one-writes at most.
        """
        if self and self[0].workflow_state_field in vals:
            wstate = vals.get(self[0].workflow_state_field)
            if wstate == self[0].workflow_signal:
                for rec in self:
                    rec.approve_step()
                    if rec.current_step:
                        vals[rec.workflow_state_field] = rec.workflow_state
                    super(ExtendedApprovalWorkflowMixin, rec).write(vals)
                return True
        return super().write(vals)
