# -*- coding: utf-8 -*-
from openerp import api, models


class ExtendedApprovalWorkflowMixin(models.AbstractModel):
    _name = 'extended.approval.workflow.mixin'
    _inherit = 'extended.approval.mixin'

    workflow_signal = 'undefined'
    workflow_state_field = 'state'
    workflow_state = 'extended_approval'
    workflow_start_state = 'draft'

    def _auto_init(self, cr, context=None):
        super(ExtendedApprovalWorkflowMixin,
              self)._auto_init(cr, context=context)
        field = self._columns.get(self.workflow_state_field)
        if field:
            field.selection.append(
                (self.workflow_state, 'Approval'))

    @api.multi
    def signal_workflow(self, signal):
        self.ensure_one()

        if signal == self.workflow_signal:
            r = self.approve_step()

            if self.current_step:
                setattr(self,
                        self.workflow_state_field,
                        self.workflow_state)

            if r:
                return {self.id: {
                    'type': 'ir.actions.client',
                    'tag': 'action_warn',
                    'params': {
                        'title': r['warning'].get('title', ''),
                        'text': r['warning'].get('message', ''),
                    }
                }}

        return super(
            ExtendedApprovalWorkflowMixin,
            self).signal_workflow(signal)

    @api.multi
    def abort_approval(self):
        self.approval_history_ids.sudo().write({
            'active': False
        })
        self.write({
            'current_step': False,
            'state': self.workflow_start_state
        })
        return {}
