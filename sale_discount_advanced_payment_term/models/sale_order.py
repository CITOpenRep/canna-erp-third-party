# -*- coding: utf-8 -*-
# Copyright (C) 2016-2019 Noviat nv/sa (www.noviat.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('payment_term')
    def _onchange_payment_term_id(self):
        for line in self.order_line:
            line.sale_discount_ids = line._get_sale_discounts()
