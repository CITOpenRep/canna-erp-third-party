# Copyright (C) Onestein 2019-2020
# Copyright (C) Noviat 2020
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ExtendedApprovalHistory(models.Model):
    _inherit = "extended.approval.history"

    source = fields.Reference(selection_add=[("account.move", "Invoice")])
