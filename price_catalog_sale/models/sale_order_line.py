# Copyright 2020 Onestein B.V.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrderLine(models.Model):
    """Override SaleOrderLine to show catalogs prices."""

    _inherit = "sale.order.line"

    currency_id = fields.Many2one(depends=["order_id.currency_id"])

    def _get_display_price(self, product):
        """Override to use price catalogs instead of pricelists."""
        super()._get_display_price(product)
        price = self.order_id.price_catalog_id.get_price(
            self.product_id, self.order_id.date_order
        )
        return price
