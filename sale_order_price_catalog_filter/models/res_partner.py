# Copyright 2020 Noviat.
# Copyright 2020 Onestein.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    sale_catalog_ids = fields.Many2many(
        comodel_name="price.catalog",
        relation="partner_price_catalog_sale_rel",
        column1="partner_id",
        column2="catalog_id",
        string="Customer Price Catalogs",
        domain=[("catalog_type", "=", "sale")],
        help="Specify here the list of price catalogs that can be set on a "
        "Sale Order as an alternative to the standard Price Catalog.",
    )
