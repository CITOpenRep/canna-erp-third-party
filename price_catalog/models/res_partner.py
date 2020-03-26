# Copyright 2020 Onestein B.V.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    """Inherit partner to add Price Catalog features."""

    _inherit = "res.partner"

    sale_catalog_ids = fields.Many2many(
        comodel_name="price.catalog",
        relation="partner_price_catalog_sale_rel",
        column1="partner_id",
        column2="catalog_id",
        string="Customer Price Catalogs",
        domain=[("catalog_type", "=", "sale")],
    )
    purchase_catalog_ids = fields.Many2many(
        comodel_name="price.catalog",
        relation="partner_price_catalog_purchase_rel",
        column1="partner_id",
        column2="catalog_id",
        string="Supplier Price Catalogs",
        domain=[("catalog_type", "=", "purchase")],
    )
