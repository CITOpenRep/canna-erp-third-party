# Copyright 2020 Onestein B.V.
# Copyright 2020 Noviat
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    """Override SaleOrder for picking catalogs."""

    _inherit = "sale.order"

    currency_id = fields.Many2one(related="price_catalog_id.currency_id")
    price_catalog_id = fields.Many2one(
        string="Price Catalog",
        comodel_name="price.catalog",
        domain=[("catalog_type", "=", "sale")],
        required=True,
        default=lambda r: r._default_price_catalog_id(),
    )

    def _default_price_catalog_id(self):
        return (
            self.env.ref("price_catalog.price_catalog_default", False)
            and self.env.ref("price_catalog.price_catalog_default")
            or self.env["price.catalog"]
        )

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        res = super().onchange_partner_id()
        self.price_catalog_id = self.partner_id.commercial_partner_id.sale_catalog_id
        return res
