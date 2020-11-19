# Copyright 2009-2020 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountGroup(models.Model):
    _inherit = "account.group"

    # the group_analytic_dimension_policy field is set via
    # the User Interface whereas the computed analytic_dimension_policy
    # is used to determine the actual group policy which can also be set
    # higher in the parent_id chain.
    group_analytic_dimension_policy = fields.Selection(
        selection=[
            ("optional", "Optional"),
            ("always", "Always"),
            ("posted", "Posted moves"),
            ("never", "Never"),
        ],
        string="Default Analytic Dimensions Policy",
        default=lambda self: self._default_analytic_dimension_policy(),
        help=(
            "Sets the default policy for analytic dimensions.\n"
            "If you select:\n"
            "- Optional: The user is free to set the analytic dimensions "
            "on account move lines with this type of account.\n"
            "- Always: The user must set the analytic dimensions.\n"
            "- Posted moves: The user will get an error message if no "
            "analytic dimensions are defined when the move is posted.\n"
            "- Never: The user should not set the analytic dimensions."
        ),
    )
    analytic_dimension_policy = fields.Selection(
        selection=[
            ("optional", "Optional"),
            ("always", "Always"),
            ("posted", "Posted moves"),
            ("never", "Never"),
        ],
        string="Effective default Analytic Dimensions Policy",
        compute="_compute_analytic_dimension_policy",
        store=True,
    )
    group_analytic_dimension_ids = fields.Many2many(
        comodel_name="analytic.dimension",
        string="Analytic Dimensions",
        help=(
            "Select the dimensions on which the Analytic Dimension Policy "
            "will be enforced."
        ),
    )
    analytic_dimensions = fields.Char(
        string="Effective default Analytic Dimensions",
        compute="_compute_analytic_dimensions",
        store=True,
    )

    @api.model
    def _default_analytic_dimension_policy(self):
        return False

    @api.depends(
        "group_analytic_dimension_policy", "parent_id.analytic_dimension_policy"
    )
    def _compute_analytic_dimension_policy(self):
        for group in self:
            group.analytic_dimension_policy = (
                group.get_analytic_dimension_policy_recursively()
            )

    def get_analytic_dimension_policy_recursively(self):
        self.ensure_one()
        res = False
        if self.group_analytic_dimension_policy:
            res = self.group_analytic_dimension_policy
        elif self.parent_id:
            res = self.parent_id.get_analytic_dimension_policy_recursively()
        return res

    @api.depends("group_analytic_dimension_ids", "parent_id.analytic_dimensions")
    def _compute_analytic_dimensions(self):
        for group in self:
            group.analytic_dimensions = group.get_analytic_dimensions_recursively()

    def get_analytic_dimensions_recursively(self):
        self.ensure_one()
        analytic_dimensions = False
        if self.group_analytic_dimension_ids:
            analytic_dimensions = ",".join(
                [x.name for x in self.group_analytic_dimension_ids]
            )
        elif self.parent_id:
            analytic_dimensions = self.parent_id.get_analytic_dimensions_recursively()
        return analytic_dimensions
