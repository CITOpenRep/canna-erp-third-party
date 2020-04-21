# Copyright 2019 Noviat.
# Copyright (C) 2020-TODAY Serpent Consulting Services Pvt. Ltd. (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        for so in self:
            if so.sale_order_group_id:
                for so2 in so.sale_order_group_id.sale_order_ids:
                    so2.compute_discount()
        return res
