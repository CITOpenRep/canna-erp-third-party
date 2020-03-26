# Copyright 2020 Onestein B.V.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    """Override PurchaseOrder for catalog prices."""

    _inherit = "purchase.order"

    price_catalog_id = fields.Many2one(
        string="Price Catalog",
        comodel_name="price.catalog",
        domain=[("catalog_type", "=", "purchase")],
    )

    @api.onchange("price_catalog_id")
    def _onchange_catalog(self):
        """When the Price Catalog field is changed, set the Order's currency
        to match that of the Price Catalog.
        """
        # Note: cascades to lines
        self.currency_id = self.price_catalog_id.currency_id


class PurchaseOrderLine(models.Model):
    """Override PurchaseOrderLine for catalog prices."""

    _inherit = "purchase.order.line"

    @api.onchange("product_qty", "product_uom")
    def _onchange_quantity(self):
        """Override method to use catalog prices instead of price lists."""
        res = super()._onchange_quantity()
        self.price_unit = self.order_id.price_catalog_id.get_price(
            self.product_id, self.order_id.date_order
        )
        return res
