# Copyright 2009-2020 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountAccountType(models.Model):
    _inherit = "account.account.type"

    analytic_dimension_policy = fields.Selection(
        selection=[
            ("optional", "Optional"),
            ("always", "Always"),
            ("posted", "Posted moves"),
            ("never", "Never"),
        ],
        string="Default Analytic Dimensions Policy",
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
