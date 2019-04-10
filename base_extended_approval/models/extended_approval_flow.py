# -*- coding: utf-8 -*-
from openerp import api, fields, models
from .extended_approval_mixin import ExtendedApprovalMixin


class ExtendedApprovalFlow(models.Model):
    _name = 'extended.approval.flow'
    _order = 'sequence'

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

        def _get_subclasses(cls):
            for sc in cls.__subclasses__():
                for ssc in _get_subclasses(sc):
                    yield ssc
                yield sc

        return [
            (x, x) for x in
            list(set([
                c._name for c in
                _get_subclasses(ExtendedApprovalMixin)
                if issubclass(c, models.Model)
                and hasattr(c, '_name')]))]

    @staticmethod
    def _recompute_next_approvers(models):
        """Do an empty write to the provided models to trigger an update of the
        Next Approver Role(s) field on records of these models which are in
        the approval process state."""
        if models == set([]):
            return
        # Bypass __iter__
        if len(models) == 0:
            models = set([models, 'pass'])
        for model in models:
            if type(model) == str and model == 'pass':
                continue
            recompute_state = model.workflow_start_state
            records = model.search(
                [('state', 'in', [recompute_state])]
            )
            records.write({})

    @api.multi
    def write(self, values):
        models = set()
        r = super(ExtendedApprovalFlow, self).write(values)
        if values.get('sequence'):
            for flow in self:
                models.add(self.env[self.model])
            self._recompute_next_approvers(models)
        return r

    @api.multi
    def unlink(self):
        models = set()
        for flow in self:
            models.add(flow.env[flow.model])
            super(ExtendedApprovalFlow, flow).unlink()
        self._recompute_next_approvers(models)
        return True
