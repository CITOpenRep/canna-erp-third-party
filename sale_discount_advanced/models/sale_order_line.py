# -*- coding: utf-8 -*-
# Copyright (C) 2015 ICTSTUDIO (<http://www.ictstudio.eu>).
# Copyright (C) 2016-2019 Noviat nv/sa (www.noviat.com).
# Copyright (C) 2016 Onestein (http://www.onestein.eu/).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openerp import api, fields, models

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    sale_discount_ids = fields.Many2many(
        comodel_name='sale.discount',
        relation='sale_line_sale_discount_rel',
        column1='sale_line_id',
        column2='discount_id',
        string='Discount Engine(s)'
    )

    def product_id_change(
            self, cr, uid, ids, pricelist_id, product_id, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False,
            fiscal_position=False, flag=False, context=None):
        res = super(SaleOrderLine, self).product_id_change(
            cr, uid, ids, pricelist_id, product_id, qty=qty, uom=uom,
            qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
            lang=lang, update_tax=update_tax, date_order=date_order,
            packaging=packaging, fiscal_position=fiscal_position,
            flag=flag, context=context)
        if product_id:
            disc_ids = self._get_sale_discount_ids(
                cr, uid, pricelist_id, date_order, product_id,
                context=context)
            res['value'].update(sale_discount_ids=[(6, 0, disc_ids)])
        return res

    def _get_sale_discount_ids(self, cr, uid, pricelist_id,
                               date_order, product_id, context=None):
        """
        v7 api.
        By default sale order lines without products are not
        included in the discount calculation.
        You can still add a discount manually to such a line or
        add non-product lines via an inherit on this method.
        """
        if context is None:
            context = {}
        self.env = api.Environment(cr, uid, context)
        discounts = self.env['sale.discount']
        pricelist = self.env['product.pricelist'].browse(pricelist_id)
        if pricelist:
            for discount in pricelist._get_active_sale_discounts(date_order):
                if product_id not in discount._get_excluded_products()._ids:
                    filter = discount._get_included_products()._ids
                    if not filter or (filter and product_id in filter):
                        discounts += discount
        return discounts._ids

    def _get_sale_discounts(self):
        """
        v8 api.
        By default sale order lines without products are not
        included in the discount calculation.
        You can still add a discount manually to such a line or
        add non-product lines via an inherit on this method.
        """
        discounts = self.env['sale.discount']
        pricelist = self.order_id.pricelist_id
        if pricelist:
            active_discounts = pricelist._get_active_sale_discounts(
                self.order_id.date_order)
            for discount in active_discounts:
                if self.product_id not in discount._get_excluded_products():
                    filter = discount._get_included_products()
                    if not filter or (filter and self.product_id in filter):
                        discounts += discount
        return discounts

    @api.onchange('product_id')
    def _onchange_sale_discount(self):
        """
        The '@api.onchange' has no effect installing this module
        on a standard Odoo V8 system due to presence of
        old style onchange ('product_id_change').
        """
        self.sale_discount_ids = self._get_sale_discounts()
        self.discount = 0.0
