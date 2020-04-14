# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    sale_discount_ids = fields.Many2many(
        "sale.discount",
        "sale_line_sale_discount_rel",
        "sale_line_id",
        "discount_id",
        string="Discount Engine(s)",
        help="Discount engines used for sale order line " "discount calculation.",
    )
    applied_sale_discount_ids = fields.Many2many(
        "sale.discount",
        "sale_line_applied_sale_discount_rel",
        "sale_line_id",
        "discount_id",
        string="Discount Engine(s)",
        readonly=True,
        help="This field contains the subset of the discount enginges "
        "with a calculated discount amount > 0.",
    )

    @api.onchange("product_id")
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        if self.product_id:
            disc_ids = self._get_sale_discount_ids(
                self.product_id, self.order_id.date_order
            )
            if disc_ids:
                self.sale_discount_ids = [(6, 0, disc_ids)]
        return res

    def _get_sale_discount_ids(self, product_id, date_order):
        """
        v7 api.
        By default sale order lines without products are not
        included in the discount calculation.
        You can still add a discount manually to such a line or
        add non-product lines via an inherit on this method.
        """
        if not product_id:
            return []
        context = self._context

        discount_ctx = context.get("discount_ids")
        if not discount_ctx:
            return []
        discount_ids = discount_ctx[0][2]
        discounts = self.env["sale.discount"]
        so_discounts = self.env["sale.discount"].browse(discount_ids)
        product = self.env["product.product"].browse(product_id)
        for discount in so_discounts:
            if discount._check_product_filter(product) and discount._check_active_date(
                check_date=date_order
            ):
                discounts += discount
        return discounts.ids

    def _get_sale_discounts(self):
        """
        v8 api.
        By default sale order lines without products are not
        included in the discount calculation.
        You can still add a discount manually to such a line or
        add non-product lines via an inherit on this method.
        """
        self.ensure_one()
        discounts = self.env["sale.discount"]
        if not self.product_id:
            return discounts
        date_order = self.order_id.date_order
        for discount in self.order_id.discount_ids:
            if discount._check_product_filter(
                self.product_id
            ) and discount._check_active_date(check_date=date_order):
                discounts += discount
        return discounts
