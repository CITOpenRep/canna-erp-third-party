# -*- coding: utf-8 -*-
from openerp import api, fields, models
from openerp.tools import safe_eval


class ExtendedApprovalFlow(models.Model):
    _name = 'extended.approval.flow'

    name = fields.Char(
        string="Name")

    sequence = fields.Integer(
        string='Priority',
        default=10)

    model = fields.Selection(
        string="Model name",
        selection="_get_extended_approval_models")

    domain = fields.Char(
        string="Domain for this flow")

    signal_name = fields.Char(
        string="Signal",
        help="If specified this workflow signal will "
        "start the extended approval.")

    steps = fields.One2many(
        comodel_name='extended.approval.step',
        inverse_name='flow_id',
        string="Steps")

    @api.model
    def _get_extended_approval_models(self):
        return []
