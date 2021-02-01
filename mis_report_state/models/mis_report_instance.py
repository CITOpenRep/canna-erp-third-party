# Copyright (C) 2020-TODAY Serpent Consulting Services Pvt. Ltd.
#    (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class MisReportInstance(models.Model):
    _inherit = "mis.report.instance"

    state = fields.Selection(
        selection=[
            ("new", "New"),
            ("ready", "Ready"),
            ("cancel", "Cancelled"),
        ],
        default="new",
        string="state",
        tracking=True
    )
