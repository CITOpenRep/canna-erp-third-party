# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    sale_discount_ids = fields.Many2many(
        "sale.discount",
        "partner_sale_discount_rel",
        "partner_id",
        "discount_id",
        string="Sale Discounts",
    )

    def _get_active_sale_discounts(self, date_order):
        self.ensure_one()
        discounts = self.env["sale.discount"]
        for discount in self.sale_discount_ids:
            if discount.active and discount._check_active_date(date_order):
                discounts += discount
        return discounts
