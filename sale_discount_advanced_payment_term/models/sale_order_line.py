# -*- coding: utf-8 -*-
# Copyright (C) 2016-2019 Noviat nv/sa (www.noviat.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import logging

from openerp import api, models

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _get_sale_discount_ids(self, cr, uid, product_id, date_order,
                               context=None):
        res = super(SaleOrderLine, self)._get_sale_discount_ids(
            cr, uid, product_id, date_order, context=context)
        if not product_id:
            return []
        if context is None:
            context = {}
        self.env = api.Environment(cr, uid, context)
        discounts = self.env['sale.discount']
        if context.get('payment_term_id'):
            self.env = api.Environment(cr, uid, context)
            payterm = self.env['account.payment.term'].browse(
                context['payment_term_id'])
            product = self.env['product.product'].browse(product_id)
            for discount in payterm._get_active_sale_discounts(date_order):
                if discount._check_product_filter(product):
                    discounts += discount
        return res + discounts.ids

    def _get_sale_discounts(self):
        res = super(SaleOrderLine, self)._get_sale_discounts()
        if not self.product_id:
            return res
        discounts = self.env['sale.discount']
        payterm = self.order_id.payment_term
        if payterm:
            active_discounts = payterm._get_active_sale_discounts(
                self.order_id.date_order)
            for discount in active_discounts:
                if discount._check_product_filter(self.product_id):
                    discounts += discount
        return res + discounts
