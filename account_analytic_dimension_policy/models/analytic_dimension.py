# Copyright 2009-2020 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AnalyticDimension(models.Model):
    _name = "analytic.dimension"
    _description = "Analytic Dimensions"

    name = fields.Selection(selection="_selection_name")
    description = fields.Text()
    company_id = fields.Many2one(comodel_name="res.company", string="Company")

    @api.model
    def _selection_name(self):
        aml_fields = self.env["account.move.line"]._fields
        select = [
            (fld, aml_fields[fld].string)
            for fld in aml_fields
            if fld not in self._dimension_blacklist()
            and aml_fields[fld].type in ("many2one", "many2many", "selection")
            and not aml_fields[fld].compute
        ]
        return select

    def _dimension_blacklist(self):
        """
        List of fields that cannot be selected as an analytic dimension.
        """
        blacklist = models.MAGIC_COLUMNS + [self.CONCURRENCY_CHECK_FIELD]
        blacklist += [
            "move_id",
            "account_id",
            "currency_id",
            "reconcile_model_id",
            "payment_id",
            "statement_line_id",
            "tax_repartition_line_id",
            "full_reconcile_id",
            "display_type",
        ]
        return blacklist

    @api.constrains("name", "company_id")
    def _check_name_unique(self):
        for rec in self:
            dims = self.search_count(
                [
                    ("name", "=", rec.name),
                    "|",
                    ("company_id", "=", rec.company_id.id),
                    ("company_id", "=", False),
                ]
            )
            if dims > 1:
                raise UserError(_("The dimension has already been defined."))

    @api.model_create_multi
    def create(self, vals_list):
        dims = super().create(vals_list)
        user_types = self.env["account.account.type"].search([])
        user_types.update({"analytic_dimension_ids": [(4, x) for x in dims.ids]})
        return dims

    def unlink(self):
        for (model, fld) in [
            ("account.account.type", "analytic_dimension_ids"),
            ("account.group", "group_analytic_dimension_ids"),
            ("account.account", "account_analytic_dimension_ids"),
        ]:
            for dim in self:
                objects = self.env[model].search([(fld, "=", dim.id)])
                objects.update({fld: [(3, dim.id)]})
        return super().unlink()
