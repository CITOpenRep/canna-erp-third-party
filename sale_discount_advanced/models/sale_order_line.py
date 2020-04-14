# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    sale_discount_ids = fields.Many2many(
        comodel_name="sale.discount",
        relation="sale_line_sale_discount_rel",
        column1="sale_line_id",
        column2="discount_id",
        string="Discount Engine(s)",
        help="Discount engines used for sale order line discount calculation.",
    )
    applied_sale_discount_ids = fields.Many2many(
        comodel_name="sale.discount",
        relation="sale_line_applied_sale_discount_rel",
        column1="sale_line_id",
        column2="discount_id",
        string="Discount Engine(s)",
        readonly=True,
        help="This field contains the subset of the discount enginges "
        "with a calculated discount amount > 0.",
    )

    @api.onchange("product_id")
    def product_id_change(self):
        res = super().product_id_change()
        if self.product_id:
            self.sale_discount_ids = self._get_sale_discounts()
        return res

    def _get_sale_discounts(self):
        """
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
