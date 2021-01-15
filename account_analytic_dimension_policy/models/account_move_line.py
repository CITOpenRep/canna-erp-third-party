# Copyright 2009-2020 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import table_exists

_logger = logging.getLogger(__name__)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    analytic_dimension_policy = fields.Selection(
        string="Policy for analytic dimension",
        related="account_id.analytic_dimension_policy",
        readonly=True,
    )
    analytic_dimensions = fields.Char(
        related="account_id.analytic_dimensions", readonly=True
    )

    @api.onchange("analytic_dimension_policy")
    def _onchange_analytic_dimension_policy(self):
        dims = self._get_analytic_dimensions()
        if self.analytic_dimension_policy == "never":
            for dim in dims:
                setattr(self, dim, False)

    @classmethod
    def _build_model(cls, pool, cr):
        """
        Add *_ui_modifier fields (* = dimension field name) to facilitate
        UI policy enforcement.
        """
        # cr.execute since ORM methods not yet fully available
        if table_exists(cr, "analytic_dimension"):
            cr.execute("SELECT name FROM analytic_dimension")
            dims = [x[0] for x in cr.fetchall()]
            for dim in dims:
                fld = "{}_ui_modifier".format(dim)
                dim_fld = fields.Selection(
                    selection=[("required", "required"), ("readonly", "readonly")],
                    compute="_compute_analytic_dimension_ui_modifier",
                )
                setattr(cls, fld, dim_fld)
        return super()._build_model(pool, cr)

    @api.depends("analytic_dimension_policy", "parent_state")
    def _compute_analytic_dimension_ui_modifier(self):
        for aml in self:
            if aml.analytic_dimension_policy == "never":
                ui_modifier = "readonly"
            elif aml.analytic_dimension_policy == "always" and aml.parent_state not in (
                "posted",
                "cancel",
            ):
                ui_modifier = "required"
            else:
                ui_modifier = False
            dims = aml._get_analytic_dimensions()
            for dim in dims:
                fld = "{}_ui_modifier".format(dim)
                setattr(aml, fld, ui_modifier)
            all_dims = self._get_all_analytic_dimensions(aml.company_id.id)
            for dim in [x for x in all_dims if x not in dims]:
                fld = "{}_ui_modifier".format(dim)
                setattr(aml, fld, False)

    @api.model_create_multi
    def create(self, vals_list):
        amls = super().create(vals_list)
        amls._check_analytic_dimension_policy()
        return amls

    def write(self, vals):
        res = super().write(vals)
        amls = self.browse(self.ids)
        amls._check_analytic_dimension_policy()
        return res

    @api.model
    def get_analytic_dimension_fields(self, company_id):
        """
        Method called by reconciliation widget.
        Returns field definitions for use by js makeRecord function.
        """
        dims = self._get_all_analytic_dimensions(company_id)
        fields_info = []
        for dim in dims:
            fields_info.append(
                {
                    "name": dim,
                    "type": self._fields[dim].type,
                    "string": self._fields[dim].string,
                    "relation": self._fields[dim].comodel_name,
                    "domain": self._fields[dim].domain,
                }
            )
        return fields_info

    def _get_analytic_dimensions(self):
        self.ensure_one()
        all_dims = self._get_all_analytic_dimensions(self.company_id.id)
        aml_dims = self.analytic_dimensions
        dims = aml_dims and [str(x) for x in aml_dims.split(",")] or all_dims
        return dims

    def _get_all_analytic_dimensions(self, company_id):
        dims = self.env["analytic.dimension"].search_read(
            domain=["|", ("company_id", "=", company_id), ("company_id", "=", False)],
            fields=["name"],
        )
        return [x["name"] for x in dims]

    def _check_analytic_dimension_policy(self):
        for aml in self:
            dims = aml._get_analytic_dimensions()
            if not dims:
                continue
            policy = aml.analytic_dimension_policy
            if not policy or policy == "optional":
                continue
            am = aml.move_id
            err_msg = _(
                "Analytic Dimension Policy violation in Journal Item ID %s, "
                "Journal Entry %s:\n"
            ) % (aml.id, am.name_get()[0][1])
            for dim in dims:
                if aml[dim] and policy == "never":
                    raise UserError(err_msg + _("Field '%s' must not be set.") % dim)
                elif not aml[dim] and (
                    policy == "always" or (policy == "posted" and am.state == "posted")
                ):
                    raise UserError(err_msg + _("Field '%s' must be set.") % dim)
