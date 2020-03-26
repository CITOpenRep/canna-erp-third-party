# Copyright 2020 Onestein B.V.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PriceCatalogItem(models.Model):
    """Holds prices of products in the subcatalog.

    NOTE:
    This model design does not support updating of prices within periods.
    Doing so would mean loss of history.
    This is a deliberate choice.
    Wer recommed to group your product carefully in subcatalogs
    and upload prices in a new subcatalog when prices need to be updated.
    """

    _name = "price.catalog.item"
    _description = "Price Catalog Item"
    _order = "id desc"
    _sql_constraints = [
        (
            "price_catalog_item_uniq",
            "unique(subcatalog_id, product_id)",
            "The Product already exists in this Subcatalog.",
        )
    ]

    company_id = fields.Many2one(
        related="subcatalog_id.company_id", store=True, readonly=True, Index=True
    )
    product_id = fields.Many2one(comodel_name="product.product", required=True)
    price = fields.Float(digits="Product Price")
    subcatalog_id = fields.Many2one(comodel_name="price.subcatalog", required=True)
