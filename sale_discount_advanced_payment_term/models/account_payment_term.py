# -*- coding: utf-8 -*-
# Copyright (C) 2016-2019 Noviat nv/sa (www.noviat.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    sale_discount_ids = fields.Many2many(
        string='Sale Discounts',
        comodel_name='sale.discount',
        relation='payterm_sale_discount_rel',
        column1='payterm_id',
        column2='discount_id')

    @api.multi
    def _get_active_sale_discounts(self, date_order):
        self.ensure_one()
        discounts = self.env['sale.discount']
        for discount in self.sale_discount_ids:
            if discount.active and \
                    discount._check_active_date(date_order):
                discounts += discount
        return discounts
