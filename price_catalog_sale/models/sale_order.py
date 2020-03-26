# Copyright 2020 Onestein B.V.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):
    """Override SaleOrder for picking catalogs."""

    _inherit = "sale.order"

    currency_id = fields.Many2one(related="price_catalog_id.currency_id")
    price_catalog_id = fields.Many2one(
        string="Price Catalog",
        comodel_name="price.catalog",
        domain=[("catalog_type", "=", "sale")],
    )
