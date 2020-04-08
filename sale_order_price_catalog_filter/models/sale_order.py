# Copyright 2020 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    allowed_price_catalog_ids = fields.Many2many(
        comodel_name="price.catalog",
        compute="_compute_allowed_price_catalog_ids",
        string="allowed price catalogs",
    )

    @api.depends(
        "partner_id.commercial_partner_id.sale_catalog_id",
        "partner_id.commercial_partner_id.sale_catalog_ids",
    )
    def _compute_allowed_price_catalog_ids(self):
        cp = self.partner_id.commercial_partner_id
        self.allowed_price_catalog_ids = cp.sale_catalog_id + cp.sale_catalog_ids
