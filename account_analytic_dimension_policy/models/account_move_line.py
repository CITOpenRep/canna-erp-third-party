# Copyright 2009-2020 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    analytic_dimension_policy = fields.Selection(
        string="Policy for analytic dimension",
        related="account_id.analytic_dimension_policy",
        readonly=True,
    )
    analytic_dimension_show = fields.Selection(
        selection=[("required", "required"), ("readonly", "readonly")],
        compute="_compute_analytic_dimension_show",
    )

    @api.onchange("analytic_dimension_policy")
    def _onchange_analytic_dimension_policy(self):
        dims = self.get_analytic_dimensions()
        if self.analytic_dimension_policy == "never":
            for dim in dims:
                setattr(self, dim, False)

    @api.depends("analytic_dimension_policy", "parent_state")
    def _compute_analytic_dimension_show(self):
        for aml in self:
            if aml.analytic_dimension_policy == "never":
                aml.analytic_dimension_show = "readonly"
            elif aml.analytic_dimension_policy == "always" and aml.parent_state not in (
                "posted",
                "cancel",
            ):
                aml.analytic_dimension_show = "required"
            else:
                aml.analytic_dimension_show = False

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
    def get_analytic_dimensions(self):
        dims = [
            fld
            for fld in self._fields
            if getattr(self._fields[fld], "analytic_dimension", False)
        ]
        return dims

    def _check_analytic_dimension_policy(self):
        dims = self.get_analytic_dimensions()
        if not dims:
            return
        for aml in self:
            policy = aml.account_id.analytic_dimension_policy
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
