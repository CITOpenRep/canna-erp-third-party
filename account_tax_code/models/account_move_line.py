# Copyright 2009-2020 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    compute_tax_codes = fields.Char(string="Tax Codes", compute="_compute_tax_codes")

    @api.depends("tax_ids", "tax_line_id")
    def _compute_tax_codes(self):
        for line in self:
            taxes = line.tax_ids + line.tax_line_id
            tax_codes = [x for x in taxes.mapped("code") if x]
            line.compute_tax_codes = ",".join(tax_codes)
