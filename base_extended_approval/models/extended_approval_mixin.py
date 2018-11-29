# -*- coding: utf-8 -*-
from openerp import _, api, fields, models
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

    approval_allowed = fields.Boolean(
        string='Approval allowed',
        compute='_compute_approval_allowed',
        help="This option is set if you are "
             "allowed to approve this Purchase Order.")

    @api.multi
    def _compute_approval_allowed(self):
        for rec in self:
            rec.approval_allowed = rec.next_approver in self.env.user.groups_id

    @api.multi
    def _compute_history_ids(self):
        for rec in self:
            rec.approval_history_ids = self.env[
                'extended.approval.history'].search([
                    ('source', '=', '{0},{1}'.format(rec._name, rec.id))
                ])

    @api.multi
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

    @api.multi
    def _get_current_approval_step(self):
        self.ensure_one()

        if self.current_step:
            return self.current_step
        else:
            flow = self._get_applicable_approval_flow()
            for step in flow.steps:
                if step.is_applicable(self):
                    return step

        return False

    @api.multi
    def _get_next_approval_step(self, step):
        self.ensure_one()

        completed = self.approval_history_ids.mapped('step_id')
        for n_step in step.flow_id.steps:
            if n_step not in completed and n_step.is_applicable(self):
                return n_step

        return False

    @api.multi
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
                        role=step.group_id.full_name
                    ),
                }
            }

        return False

    @api.multi
    def cancel_approval(self):
        self.approval_history_ids.sudo().write({
            'active': False
        })
        self.write({
            'current_step': False,
        })
        return {}

    @api.multi
    def abort_approval(self):
        self.cancel_approval()
        return {}

    @api.multi
    def show_approval_group_users(self):
        a_users = self.next_approver.users
        a_partners = a_users.mapped('partner_id')
        ptree = self.env.ref('base.view_partner_tree')
        action = {
            'name': _('Approval Group Users'),
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_type': 'form',
            'view_mode': 'tree',
            'view_id': ptree.id,
            'domain': [('id', 'in', a_partners._ids)],
            'context': self._context,
            }
        return action
