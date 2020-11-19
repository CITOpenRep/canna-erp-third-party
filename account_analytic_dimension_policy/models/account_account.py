# Copyright 2009-2020 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountAccount(models.Model):
    _inherit = "account.account"

    # the account_analytic_dimension_policy field is set via
    # the User Interface whereas the computed analytic_dimension_policy
    # is used to determine the actual policy which can also be set
    # on Account Group or Account Type.
    account_analytic_dimension_policy = fields.Selection(
        selection=[
            ("optional", "Optional"),
            ("always", "Always"),
            ("posted", "Posted moves"),
            ("never", "Never"),
        ],
        string="Account Analytic Dimensions Policy",
        help=(
            "Overrule the Analytic Dimensions Policy as defined on "
            "Account Group or Account Type.\n"
            "If you select:\n"
            "- Optional: The user is free to set the analytic dimensions "
            "on account move lines with this type of account.\n"
            "- Always: The user must set the analytic dimensions.\n"
            "- Posted moves: The user will get an error message if no "
            "analytic dimensions are defined when the move is posted.\n"
            "- Never: The user must not set the analytic dimensions."
        ),
    )
    analytic_dimension_policy = fields.Selection(
        selection=[
            ("optional", "Optional"),
            ("always", "Always"),
            ("posted", "Posted moves"),
            ("never", "Never"),
        ],
        string="Analytic Dimensions Policy",
        compute="_compute_analytic_dimension_policy",
        store=True,
        require=True,
        help=(
            "Analytic Dimensions Policy for this Account "
            "defined on Account, Account Group or Account Type."
        ),
    )
    account_analytic_dimension_ids = fields.Many2many(
        comodel_name="analytic.dimension",
        string="Account Analytic Dimensions",
        help=(
            "Overrule the Analytic Dimensions as defined on "
            "Account Group or Account Type.\n"
            "Select None to enforce all dimensions."
        ),
    )
    analytic_dimensions = fields.Char(
        string="Analytic Dimensions",
        compute="_compute_analytic_dimensions",
        store=True,
        help=(
            "Analytic Dimensions for this Account "
            "defined on Account, Account Group or Account Type."
        ),
    )

    @api.depends(
        "account_analytic_dimension_policy",
        "group_id.analytic_dimension_policy",
        "user_type_id.analytic_dimension_policy",
    )
    def _compute_analytic_dimension_policy(self):
        for account in self:
            account.analytic_dimension_policy = (
                account.account_analytic_dimension_policy
                or account.group_id.analytic_dimension_policy
                or account.user_type_id.analytic_dimension_policy
            )

    @api.depends(
        "account_analytic_dimension_ids",
        "group_id.analytic_dimensions",
        "user_type_id.analytic_dimensions",
    )
    def _compute_analytic_dimensions(self):
        for account in self:
            if account.account_analytic_dimension_ids:
                account.analytic_dimensions = ",".join(
                    [x.name for x in account.account_analytic_dimension_ids]
                )
            else:
                account.analytic_dimensions = (
                    account.group_id.analytic_dimensions
                    or account.user_type_id.analytic_dimensions
                )
