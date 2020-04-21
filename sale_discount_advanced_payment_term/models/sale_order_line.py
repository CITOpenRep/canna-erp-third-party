# Copyright (C) 2016-2019 Noviat nv/sa (www.noviat.com).
# Copyright (C) 2016 Onestein (http://www.onestein.eu/).
# Copyright (C) 2020-TODAY Serpent Consulting Services Pvt. Ltd. (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_sale_discount_ids(self, product_id, date_order):
        res = super(SaleOrderLine, self)._get_sale_discount_ids(
            self.product_id, self.order_id.date_order
        )
        if not self.product_id:
            return []
        context = self._context

        discounts = self.env["sale.discount"]
        if context.get("payment_term_id"):
            payterm = self.env["account.payment.term"].browse(
                context["payment_term_id"]
            )
            product = self.env["product.product"].browse(product_id)
            for discount in payterm._get_active_sale_discounts(date_order):
                if discount._check_product_filter(product):
                    discounts += discount
        return res + discounts.ids

    def _get_sale_discounts(self):
        res = super(SaleOrderLine, self)._get_sale_discounts()
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
