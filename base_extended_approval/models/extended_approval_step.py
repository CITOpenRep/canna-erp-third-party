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

    condition = fields.Selection(
        string="Condition",
        required=True,
        selection="_get_condition_types")

    limit = fields.Float(
        string="Amount")

    group_id = fields.Many2one(
        comodel_name='res.groups',
        string="Approver")

    @api.model
    def _get_condition_types(self):
        return [
            ('always', 'No condition'),
            ('amount_total', 'Amount Total From')
        ]

    def is_applicable(self, record):
        return getattr(
            self, '_is_applicable_' + self.condition)(
                record)

    def _is_applicable_always(self, record):
        return True

    def _is_applicable_amount_total(self, record):
        # TODO: refactor to separte class
        return record.amount_total >= self.limit
