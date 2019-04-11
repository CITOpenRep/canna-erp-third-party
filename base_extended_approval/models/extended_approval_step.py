# -*- coding: utf-8 -*-
from openerp import api, fields, models


class ExtendedApprovalStep(models.Model):
    _name = 'extended.approval.step'
    _inherit = ['extended.approval.config.mixin']
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
    def get_applicable_models(self):
        return [self.flow_id.model]

    @api.multi
    def is_applicable(self, record):
        return self.condition.is_applicable(record) \
            if self.condition else True
