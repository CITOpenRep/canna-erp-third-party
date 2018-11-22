# -*- coding: utf-8 -*-
from openerp import _, fields, models
from openerp.tools import safe_eval


class ExtendedApprovalMixin(models.AbstractModel):
    _name = 'extended.approval.mixin'

    next_approver = fields.Many2one(
        comodel_name='res.groups',
        related="current_step.group_id",
        string="Next Approver")

    current_step = fields.Many2one(
        comodel_name='extended.approval.step',
        copy=False,
        string="Current Approval Step")

    approval_history_ids = fields.One2many(
        comodel_name='extended.approval.history',
        compute="_compute_history_ids",
        readonly=True,
        copy=False,
        string='Approval History')

    def _compute_history_ids(self):
        for rec in self:
            rec.approval_history_ids = self.env[
                'extended.approval.history'].search([
                    ('source', '=', '{0},{1}'.format(rec._name, rec.id))
                ])

    def _get_applicable_approval_flow(self):
        self.ensure_one()

        flows = self.env['extended.approval.flow'].search([
            ('model', '=', self._name)
        ], order='sequence')
        for c_flow in flows:
            if self.search([
                    ('id', 'in', self._ids)
            ] + safe_eval(c_flow.domain) if c_flow.domain else []):
                return c_flow
        return False

    def _get_current_approval_step(self):
        self.ensure_one()

        if self.current_step:
            return self.current_step
        else:
            flow = self._get_applicable_approval_flow()
            return flow.steps[0] if flow.steps else False

        return False

    def _get_next_approval_step(self, step):
        self.ensure_one()

        completed = self.approval_history_ids.mapped('step_id')
        for n_step in step.flow_id.steps:
            if n_step not in completed and n_step.is_applicable(self):
                return n_step

        return False

    def approve_step(self):
        """Attempt current approval step.

        Returns False if approval is completed
        """
        self.ensure_one()

        step = self._get_current_approval_step()
        if not step:
            return False

        if step.group_id in self.env.user.groups_id:
            self.env['extended.approval.history'].create({
                'approver_id': self.env.user.id,
                'source': '{0},{1}'.format(self._name, self.id),
                'step_id': step.id,
            })

            # move to next step
            step = self._get_next_approval_step(step)

        self.current_step = step
        if step:
            return {
                'warning': {
                    'title': _('Extended approval required'),
                    'message': _('Approval by {role} required').format(
                        role = step.group_id.full_name
                    ),
                }
            }

        return False
