# Copyright 2019-2020 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _prepare_invoice(self):
        vals = super()._prepare_invoice()
        if self.env.context.get("invoice_date"):
            vals["invoice_date"] = self.env.context["invoice_date"]
        return vals

