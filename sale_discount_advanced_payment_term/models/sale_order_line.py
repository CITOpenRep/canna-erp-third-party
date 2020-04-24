# Copyright (C) 2016-2019 Noviat nv/sa (www.noviat.com).
# Copyright (C) 2016 Onestein (http://www.onestein.eu/).
# Copyright (C) 2020 Serpent Consulting Svc (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_sale_discounts(self):
        res = super()._get_sale_discounts()
        if not self.product_id:
            return res
        discounts = self.env["sale.discount"]
        payterm = self.order_id.payment_term_id
        if payterm:
            active_discounts = payterm._get_active_sale_discounts(
                self.order_id.date_order
            )
            for discount in active_discounts:
                if discount._check_product_filter(self.product_id):
                    discounts += discount
        return res + discounts
