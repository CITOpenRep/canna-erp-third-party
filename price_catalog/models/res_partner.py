# Copyright 2020 Onestein B.V.
# Copyright 2020 Noviat
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    """Inherit partner to add Price Catalog features."""

    _inherit = "res.partner"

    sale_catalog_id = fields.Many2one(
        comodel_name="price.catalog",
        string="Customer Price Catalog",
        company_dependent=True,
        domain=[("catalog_type", "=", "sale")],
    )
    purchase_catalog_id = fields.Many2one(
        comodel_name="price.catalog",
        string="Supplier Price Catalog",
        company_dependent=True,
        domain=[("catalog_type", "=", "purchase")],
    )
