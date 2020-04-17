# Copyright 2020 Onestein B.V.
# Copyright 2020 Noviat
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PriceCatalog(models.Model):
    """Price catalogs."""

    _name = "price.catalog"
    _description = "Price Catalog"
    _inherit = ["mail.thread"]
    _order = "id desc"

    name = fields.Char(required=True, tracking=True)
    active = fields.Boolean(default=True, tracking=True)
    catalog_type = fields.Selection(
        selection=[
            ("sale", "Sale Price Catalog"),
            ("purchase", "Purchase Price Catalog"),
        ],
        required=True,
    )
    company_id = fields.Many2one(comodel_name="res.company")
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        default=lambda self: self.env.company.currency_id.id,
        required=True,
    )
    subcatalog_ids = fields.One2many(
        comodel_name="price.subcatalog", inverse_name="catalog_id"
    )

    def _get_items(self, product_id, date_order):
        """Get the catalog items, ordered by the related subcatalog's sequence
        for the provided product and dates.
        Based on product._compute_price_rule_get_items()
        """
        self.env["price.catalog.item"].flush(["price", "company_id"])
        # Handle date range
        self.env.cr.execute(
            """
            SELECT item.id
            FROM price_catalog_item AS item
            INNER JOIN price_subcatalog AS subcatalog
            ON item.subcatalog_id = subcatalog.id
            WHERE
                subcatalog.active = True
                AND subcatalog.catalog_id = %s
                AND (item.product_id IN (%s))
                AND (subcatalog.start_date IS NULL
                     OR subcatalog.start_date <= %s)
                AND (subcatalog.end_date IS NULL
                     OR subcatalog.end_date >= %s)
            ORDER BY
                subcatalog.sequence, item.sequence
            """,
            (self.id, tuple(product_id.ids), date_order, date_order),
        )
        item_ids = [x[0] for x in self.env.cr.fetchall()]
        return self.env["price.catalog.item"].browse(item_ids)

    def get_price(self, product_id, date_order):
        """Get the price of the provided product depending on the order's
        date and the sequence of the found subcatalogs.
        Return False if product not in catalog.
        """
        price = False
        if not self:
            return False
        if not product_id:
            return 0.0
        price = 0.0
        items = self._get_items(product_id, date_order)
        for item in items:
            price = item.price
            break
        return price
