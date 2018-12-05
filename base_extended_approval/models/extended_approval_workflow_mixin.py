# -*- coding: utf-8 -*-
from openerp import api, models


class ExtendedApprovalWorkflowMixin(models.AbstractModel):
    _name = 'extended.approval.workflow.mixin'
    _inherit = 'extended.approval.mixin'

    workflow_signal = 'undefined'
    workflow_state_field = 'state'
    workflow_state = 'extended_approval'
    workflow_start_state = 'draft'

    @api.model
    def _setup_complete(self):
        """Add extra workflow state to the workflow_state_field """
        super(ExtendedApprovalWorkflowMixin,
              self)._setup_complete()
        field = self._columns.get(self.workflow_state_field)
        if field:
            try:
                state_names = [t[0] for t in field.selection]
                if self.workflow_state not in state_names:
                    if self.workflow_start_state in state_names:
                        field.selection.insert(
                            state_names.index(self.workflow_start_state) + 1,
                            (self.workflow_state, 'Approval'))
                    else:
                        field.selection.append(
                            (self.workflow_state, 'Approval'))
            except TypeError:
                # probably a callable selection attribute
                # TODO: decorated callable
                pass

    @api.multi
    def signal_workflow(self, signal):
        """Intercept workflow_signal and start extended approval"""
        if len(self) == 0:
            return super(
                ExtendedApprovalWorkflowMixin,
                self).signal_workflow(signal)

        self.ensure_one()

        if signal == self.workflow_signal:
            r = self.approve_step()

            if self.current_step:
                setattr(self,
                        self.workflow_state_field,
                        self.workflow_state)

            # if r:
            #     return {self.id: {
            #         'type': 'ir.actions.client',
            #         'tag': 'action_warn',
            #         'params': {
            #             'title': r['warning'].get('title', ''),
            #             'text': r['warning'].get('message', ''),
            #         }
            #     }}

            if r:
                return {self.id: False}

        return super(
            ExtendedApprovalWorkflowMixin,
            self).signal_workflow(signal)

    @api.multi
    def abort_approval(self):
        super(
            ExtendedApprovalWorkflowMixin,
            self).abort_approval()
        self.write({
            'state': self.workflow_start_state
        })
        return {}
