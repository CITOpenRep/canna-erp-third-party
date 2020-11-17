# Copyright (C) Onestein 2019-2020
# Copyright (C) Noviat 2020
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import safe_eval


class ExtendedApprovalCondition(models.Model):
    _name = "extended.approval.condition"
    _inherit = ["extended.approval.config.mixin"]
    _description = "Extended approval condition"

    name = fields.Char(string="Name", required=True)
    condition_type = fields.Selection(
        string="Type", required=True, selection="_get_condition_types"
    )
    domain = fields.Text(string="Expression")

    def get_applicable_models(self):
        return [
            step.flow_id.model
            for rec in self
            for step in self.env["extended.approval.step"].search(
                [("condition", "=", rec.id)]
            )
        ]

    @api.model
    def _get_condition_types(self):
        return [
            ("always", "No condition"),
            ("domain", "Domain condition"),
            ("expression", "Python expression"),
        ]

    def is_applicable(self, record):
        return getattr(self, "_is_applicable_" + self.condition_type)(record)

    def _is_applicable_always(self, record):
        return True

    def _is_applicable_domain(self, record):
        return record.search(
            [("id", "in", record._ids)] + safe_eval(self.domain) if self.domain else []
        )

    def _is_applicable_expression(self, record):
        return safe_eval(self.domain, {"record": record})
