# -*- coding: utf-8 -*-
from openerp import api, fields, models


class ExtendedApprovalStep(models.Model):
    _name = 'extended.approval.step'

    _order = 'sequence'

    flow_id = fields.Many2one(
        comodel_name='extended.approval.flow',
        string="Extended Approval",
        required=True)

    sequence = fields.Integer(
        string='Priority',
        default=10)

    condition = fields.Many2one(
        comodel_name='extended.approval.condition',
        string="Condition")

    limit = fields.Float(
        string="Amount")

    group_ids = fields.Many2many(
        comodel_name='res.groups',
        string="Approver")

    @api.multi
    def is_applicable(self, record):
        return self.condition.is_applicable(record) \
            if self.condition else True

    @api.multi
    def write(self, values):
        models = set()
        r = super(ExtendedApprovalStep, self).write(values)
        for step in self:
            models.add(self.env[self.flow_id.model])
        self.flow_id._recompute_next_approvers(models)
        return r

    @api.multi
    def unlink(self):
        models = set()
        flow = self.flow_id
        for step in self:
            models.add(step.env[step.flow_id.model])
            super(ExtendedApprovalStep, step).unlink()
        flow._recompute_next_approvers(models)
        return True

    @api.model
    def create(self, values):
        models = set()
        r = super(ExtendedApprovalStep, self).create(values)
        for step in r:
            models.add(step.env[step.flow_id.model])
        self.flow_id._recompute_next_approvers(models)
        return r
