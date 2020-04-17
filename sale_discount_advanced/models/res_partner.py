# Copyright (C) 2019 Noviat nv/sa (www.noviat.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    sale_discount_ids = fields.Many2many(
        comodel_name="sale.discount",
        relation="partner_sale_discount_rel",
        column1="partner_id",
        column2="discount_id",
        string="Sale Discounts",
    )

    def _get_active_sale_discounts(self, date_order):
        self.ensure_one()
        discounts = self.env["sale.discount"]
        for discount in self.sale_discount_ids:
            if discount.active and discount._check_active_date(date_order):
                discounts += discount
        return discounts
