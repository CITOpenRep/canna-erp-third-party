# Copyright 2009-2020 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountAccountType(models.Model):
    _inherit = "account.account.type"

    analytic_dimension_policy = fields.Selection(
        selection=[
            ("optional", "Optional"),
            ("always", "Always"),
            ("posted", "Posted moves"),
            ("never", "Never"),
        ],
        string="Analytic Dimensions Policy",
        default="optional",
        company_dependent=True,
        required=True,
        help=(
            "Sets the default policy for analytic dimensions.\n"
            "If you select:\n"
            "- Optional: The user is free to set the analytic dimensions "
            "on account move lines with this type of account.\n"
            "- Always: The user must set the analytic dimensions.\n"
            "- Posted moves: The user will get an error message if no "
            "analytic dimensions are defined when the move is posted.\n"
            "- Never: The user should not set the analytic dimensions.\n\n"
            "This field is company dependent.\n"
            "This default can be overruled via the Analytic Dimension Policy field on "
            "Account Groups and Accounts."
        ),
    )
    analytic_dimension_ids = fields.Many2many(
        comodel_name="analytic.dimension",
        string="Analytic Dimensions",
        help=(
            "Select the dimensions on which the Analytic Dimension Policy "
            "will be enforced.\nSelect None to enforce all dimensions."
        ),
    )
    analytic_dimensions = fields.Char(
        string="Analytic Dimensions List",
        compute="_compute_analytic_dimensions",
        store=True,
    )

    @api.depends("analytic_dimension_ids")
    def _compute_analytic_dimensions(self):
        for rec in self:
            rec.analytic_dimensions = ",".join(
                [x.name for x in rec.analytic_dimension_ids]
            )
