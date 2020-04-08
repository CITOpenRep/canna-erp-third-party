# Copyright 2020 Onestein B.V.
# Copyright 2020 Noviat
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PriceSubcatalog(models.Model):
    """Collects product prices valid for a certain period."""

    _name = "price.subcatalog"
    _description = "Price Subcatalog"
    _inherit = ["mail.thread"]
    _order = "start_date desc, sequence"

    name = fields.Char(required=True, tracking=True)
    active = fields.Boolean(default=True, tracking=True)
    sequence = fields.Integer(
        help="Open the and edit the Catalog to change the sequence using the "
        "handle widget, which is the first column of the Subcatalog list. The "
        "highest Subcatalog in the list will be scanned through for prices "
        "first. In other words: the lower the number on this field, the "
        "higher in the list Subcatalog will appear, which elevates the "
        "priority of prices to be looked up."
    )
    start_date = fields.Date()
    end_date = fields.Date()
    item_ids = fields.One2many(
        comodel_name="price.catalog.item", inverse_name="subcatalog_id"
    )
    catalog_id = fields.Many2one(
        comodel_name="price.catalog", string="Price Catalog", required=True
    )
    catalog_type = fields.Selection(related="catalog_id.catalog_type", store=True)
    catalog_type_filter = fields.Selection(
        selection=[
            ("sale", "Sale Price Catalog"),
            ("purchase", "Purchase Price Catalog"),
        ]
    )
    company_id = fields.Many2one(
        related="catalog_id.company_id", store=True, readonly=True, Index=True
    )
