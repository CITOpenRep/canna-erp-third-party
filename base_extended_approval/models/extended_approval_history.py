# Copyright (C) 2020-TODAY SerpentCS Pvt. Ltd. (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ExtendedApprovalHistory(models.Model):
    _name = "extended.approval.history"
    _order = "date asc"
    _rec_name = "date"

    active = fields.Boolean(
        string="Active",
        default=True,
        help="Approval is part of the " "current approval process.",
    )

    approver_id = fields.Many2one(
        comodel_name="res.users", string="Approver", readonly=True
    )

    step_id = fields.Many2one(
        comodel_name="extended.approval.step", string="Step", readonly=True
    )

    requested_group_ids = fields.Many2many(
        comodel_name="res.groups",
        related="step_id.group_ids",
        string="Requested",
        readonly=True,
    )

    date = fields.Datetime(
        readonly=True, default=fields.Datetime.now, string="Approval date"
    )

    source = fields.Reference(selection=[], string="Source")
