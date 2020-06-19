# Copyright (C) 2020-TODAY SerpentCS Pvt. Ltd. (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ExtendedApprovalHistory(models.Model):
    _inherit = "extended.approval.history"

    source = fields.Reference(selection_add=[('purchase.order', 'Purchase Order')])
