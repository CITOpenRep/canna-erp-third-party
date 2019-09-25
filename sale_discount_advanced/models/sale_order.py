# -*- coding: utf-8 -*-
# Copyright (C) 2015 ICTSTUDIO (<http://www.ictstudio.eu>).
# Copyright (C) 2016-2019 Noviat nv/sa (www.noviat.com).
# Copyright (C) 2016 Onestein (http://www.onestein.eu/).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from lxml import etree

from openerp import api, fields, models
import openerp.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    discount_amount = fields.Float(
        digits=dp.get_precision('Account'),
        string='Total Discount Amount',
        readonly=True,
        store=True)
    discount_base_amount = fields.Float(
        digits=dp.get_precision('Account'),
        string='Base Amount before Discount',
        readonly=True,
        store=True,
        help="Sum of the totals of all Order Lines before discount."
             "\nAlso lines without discount are included in this total.")
    discount_ids = fields.Many2many(
        string='Sale Discount engines',
        comodel_name='sale.discount',
        relation='sale_order_discount_rel',
        column1='order_id',
        column2='discount_id',
        help="Sale Discount engines for this order.")

    @api.onchange('discount_ids')
    def _onchange_discount_ids(self):
        self.ensure_one()
        for line in self.order_line:
            discounts = line._get_sale_discounts()
            if discounts != line.sale_discount_ids:
                line.sale_discount_ids = discounts
                line.discount = 0.0

    @api.onchange('partner_id', 'date_order')
    def _onchange_sale_discount_advanced_partner_id_(self):
        res = self.onchange_partner_id(self.partner_id.id)
        if res:
            vals = res.get('value') or {}
            for k, v in vals.iteritems():
                setattr(self, k, v)
            del res['value']
        if self.partner_id:
            cpartner = self.partner_id.commercial_partner_id
            self.discount_ids = cpartner._get_active_sale_discounts(
                self.date_order)
        return res

    @api.onchange('date_order')
    def _onchange_date_order(self):
        self.ensure_one()
        if self.partner_id:
            cpartner = self.partner_id.commercial_partner_id
            old_discounts = self.discount_ids
            new_discounts = cpartner._get_active_sale_discounts(
                self.date_order)
            if old_discounts != new_discounts:
                self.discount_ids -= old_discounts
                self.discount_ids += new_discounts

    @api.model
    def create(self, vals):
        order = super(SaleOrder, self).create(vals)
        order.compute_discount()
        return order

    @api.multi
    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        for so in self:
            if not self._context.get('skip_discount_calc'):
                so.compute_discount()
        return res

    @api.model
    def fields_view_get(self, view_id=None, view_type=False,
                        toolbar=False, submenu=False):
        res = super(SaleOrder, self).fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)
        context = self._context
        if not context.get('sale_discount_advanced'):
            if view_type == 'form':
                view_obj = etree.XML(res['arch'])
                order_line = view_obj.xpath("//field[@name='order_line']")
                extra_ctx = "'sale_discount_advanced': 1, " \
                    "'discount_ids': discount_ids"
                for el in order_line:
                    ctx = el.get('context')
                    if ctx:
                        ctx_strip = ctx.rstrip("}").strip().rstrip(",")
                        ctx = ctx_strip + ", " + extra_ctx + "}"
                    else:
                        ctx = "{" + extra_ctx + "}"
                    el.set('context', str(ctx))
                    res['arch'] = etree.tostring(view_obj)
        return res

    @api.multi
    def button_dummy(self):
        res = super(SaleOrder, self).button_dummy()
        self.compute_discount()
        return res

    @api.multi
    def action_button_confirm(self):
        self.compute_discount()
        return super(SaleOrder, self).action_button_confirm()

    @api.multi
    def compute_discount(self):
        for so in self:
            if so.state not in ['draft', 'sent']:
                return
        self._update_discount()

    def _update_discount(self):
        if self._context.get('skip_discount_calc'):
            return

        grouped_discounts = {}
        base_amount_totals = {}
        line_updates = {}

        orders = self.with_context(
            dict(self._context, skip_discount_calc=True))
        for so in orders:
            total_base_amount = 0.0
            for line in so.order_line:
                base_amount = line.price_unit * line.product_uom_qty
                total_base_amount += base_amount
                for discount in line.sale_discount_ids:
                    if discount not in grouped_discounts:
                        grouped_discounts[discount] = line
                    else:
                        grouped_discounts[discount] += line
            base_amount_totals[so] = total_base_amount

        # redistribute the discount to the lines
        # when discount_base == 'sale_order' | 'sale_order_group'
        for discount, lines in grouped_discounts.iteritems():
            if discount.discount_base == 'sale_order':
                for so in orders:
                    so_lines = lines.filtered(lambda r: r.order_id == so)
                    match, pct = discount._calculate_discount(so_lines)
                    for line in so_lines:
                        if line not in line_updates:
                            line_updates[line] = [(discount, pct)]
                        else:
                            line_updates[line] += [(discount, pct)]
            else:  # 'sale_line' or 'sale_order_group'
                match, pct = discount._calculate_discount(
                    lines=lines)
                for line in lines:
                    if line not in line_updates:
                        line_updates[line] = [(discount, pct)]
                    else:
                        line_updates[line] += [(discount, pct)]

        line_update_vals = {}
        for line, line_discounts in line_updates.iteritems():
            discount_ids = [x[0].id for x in line_discounts]
            line_update_vals[line] = {
                'sale_discount_ids': [(6, 0, discount_ids)]}
            pct_sum = 0.0
            exclusives = [x for x in line_discounts if x[0].exclusive and x[1]]
            if exclusives:
                exclusives.sort(key=lambda x: x[0].sequence)
                exclusive = exclusives[0]
                pct_exclusive = min(exclusive[1], 100)
                if exclusive[0].exclusive == 'highest':
                    pct_other = sum(
                        [x[1] for x in line_discounts if x not in exclusives])
                    pct_other = min(pct_other, 100.0)
                    if pct_other > pct_exclusive:
                        applied_discount_ids = [
                            x[0].id for x in line_discounts
                            if x not in exclusives and x[1]]
                        line_update_vals[line] = {
                            'discount': pct_other,
                            'applied_sale_discount_ids': [
                                (6, 0, applied_discount_ids)],
                        }
                    else:
                        applied_discount_ids = exclusive[0].ids
                        line_update_vals[line] = {
                            'discount': pct_exclusive,
                            'applied_sale_discount_ids': [
                                (6, 0, applied_discount_ids)],
                        }
                else:
                    applied_discount_ids = exclusive[0].ids
                    line_update_vals[line] = {
                        'discount': pct_exclusive,
                        'applied_sale_discount_ids': [
                            (6, 0, applied_discount_ids)],
                    }
            else:
                pct_sum = sum([x[1] for x in line_discounts])
                pct_sum = min(pct_sum, 100.0)
                applied_discount_ids = [
                    x[0].id for x in line_discounts if x[1]]
                line_update_vals[line] = {
                    'discount': pct_sum,
                    'applied_sale_discount_ids': [
                        (6, 0, applied_discount_ids)],
                }

        for line in line_update_vals:
            line.write(line_update_vals[line])

        for so in orders:
            vals = {}
            total_discount_amount = 0.0
            for line in so.order_line:
                base_amount = line.price_unit * line.product_uom_qty
                discount_pct = line.discount
                total_discount_amount += base_amount * discount_pct / 100.0
            if not so.currency_id.is_zero(
                    so.discount_amount - total_discount_amount):
                vals['discount_amount'] = total_discount_amount
            if not so.currency_id.is_zero(
                    so.discount_base_amount - base_amount_totals[so]):
                vals['discount_base_amount'] = base_amount_totals[so]
            if vals:
                so.write(vals)
