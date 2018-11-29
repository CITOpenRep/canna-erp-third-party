# -*- coding: utf-8 -*-
# Copyright (C) 2015 ICTSTUDIO (<http://www.ictstudio.eu>).
# Copyright (C) 2016-2018 Noviat nv/sa (www.noviat.com).
# Copyright (C) 2016 Onestein (http://www.onestein.eu/).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from openerp import api, fields, models, _
from openerp.exceptions import Warning as UserError

_logger = logging.getLogger(__name__)


class SaleDiscount(models.Model):
    _name = 'sale.discount'
    _inherit = 'mail.thread'
    _order = 'sequence'
    _track = {
        'active': {
            'sale_discount_advanced.mt_discount_active':
                lambda self, cr, uid, obj, ctx=None: True,
        },
        'start_date': {
            'sale_discount_advanced.mt_discount_start_date':
                lambda self, cr, uid, obj, ctx=None: True,
        },
        'end_date': {
            'sale_discount_advanced.mt_discount_end_date':
                lambda self, cr, uid, obj, ctx=None: True,
        },
    }

    sequence = fields.Integer()
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.user.company_id)
    name = fields.Char(
        string='Discount',
        track_visibility='onchange',
        required=True)
    start_date = fields.Date(
        string='Start date',
        track_visibility='onchange')
    end_date = fields.Date(
        string='End date',
        track_visibility='onchange')
    active = fields.Boolean(
        string='Discount active',
        track_visibility='onchange',
        default=lambda self: self._default_active())
    discount_base = fields.Selection(
        selection=lambda self: self._selection_discount_base(),
        string='Discount Base',
        required=True,
        default='sale_order',
        track_visibility='onchange',
        help="Base the discount on ")
    pricelist_ids = fields.Many2many(
        comodel_name='product.pricelist',
        relation='pricelist_sale_discount_rel',
        column1='discount_id',
        column2='pricelist_id',
        track_visibility='onchange')
    rule_ids = fields.One2many(
        comodel_name='sale.discount.rule',
        inverse_name='sale_discount_id',
        string='Discount Rules',
        track_visibility='onchange')
    excluded_product_category_ids = fields.Many2many(
        comodel_name='product.category',
        string='Excluded Product Categories',
        track_visibility='onchange',
        help="Products in these categories will by default be excluded "
             "from this discount.")
    excluded_product_ids = fields.Many2many(
        comodel_name='product.product',
        string='Excluded Products',
        track_visibility='onchange',
        help="These products will by default be excluded "
             "from this discount.")

    @api.model
    def _default_active(self):
        return True

    @api.model
    def _selection_discount_base(self):
        """
        Separate method to allow the removal of an option
        via inherit.
        """
        selection = [
            ('sale_order', 'Base discount on Order amount'),
            ('sale_line', 'Base discount on Line amount')]
        return selection

    @api.onchange('discount_base')
    def _onchange_discount_base(self):
        self.rule_ids.write({'matching_type': 'amount'})

    @api.model
    def create(self, vals):
        ctx = dict(self.env.context,
                   mail_create_nolog=True,
                   mail_create_nosubscribe=True,
                   skip_message_track=True)
        discount = super(SaleDiscount, self.with_context(ctx)).create(vals)
        msg = _("Discount object created")
        discount.message_post(
            body=msg,
            subtype='sale_discount_advanced.mt_discount_new')
        return discount

    @api.multi
    def unlink(self):
        if any(self.env['sale.order.line'].search(
                [('sale_discount_ids', 'in', self.ids)], limit=1)):
            raise UserError(_(
                'You cannot delete a discount which is used in a Sale Order!'))
        return super(SaleDiscount, self).unlink()

    @api.multi
    def message_track(self, tracked_fields, initial_values):
        if self.env.context.get('skip_message_track'):
            return True
        return super(SaleDiscount, self).message_track(
            tracked_fields, initial_values)

    def check_active_date(self, check_date=None):
        if not check_date:
            check_date = fields.Datetime.now()
        if self.start_date and self.end_date \
                and (check_date >= self.start_date and
                     check_date < self.end_date):
            return True
        if self.start_date and not self.end_date \
                and (check_date >= self.start_date):
            return True
        if not self.start_date and self.end_date \
                and (check_date < self.end_date):
            return True
        elif not self.start_date or not self.end_date:
            return True
        else:
            return False

    def _calculate_line_discount(self, line):
        return self._calculate_discount(line.price_unit, line.product_uom_qty,
                                        line=line)

    def _calculate_discount(self, price_unit, qty, line=None):
        base = qty * price_unit
        disc_amt = 0.0
        disc_pct = 0.0
        for rule in self.rule_ids:
            match_min = match_max = False
            if rule.matching_type == 'amount':
                base = self._round_amt(base)
                rule_min_base = self._round_amt(rule.min_base)
                rule_max_base = self._round_amt(rule.max_base)
                if rule_min_base > 0 and rule_min_base > base:
                    continue
                else:
                    match_min = True
                if rule_max_base > 0 and rule_max_base < base:
                    continue
                else:
                    match_max = True
            elif rule.matching_type == 'quantity':
                qty = self._round_qty(qty)
                rule_min_qty = self._round_qty(rule.min_qty)
                rule_max_qty = self._round_qty(rule.max_qty)
                if line and line.product_id == rule.product_id:
                    if rule_min_qty > 0 and rule_min_qty > qty:
                        continue
                    else:
                        match_min = True
                    if rule_max_qty > 0 and rule_max_qty < qty:
                        continue
                    else:
                        match_max = True
            else:
                raise NotImplementedError

            if match_min and match_max:
                if rule.discount_type == 'perc':
                    disc_amt = base * rule.discount_pct / 100.0
                    disc_pct = rule.discount_pct
                else:
                    if rule.matching_type == 'quantity':
                        disc_amt = min(rule.discount_amount_unit * qty, base)
                    else:
                        disc_amt = min(rule.discount_amount, base)
                    disc_pct = disc_amt / base * 100.0
                break
        return disc_amt, disc_pct

    def _round_amt(self, val):
        digits = self.env['sale.discount.rule']._fields['min_base'].digits[1]
        return round(val, digits)

    def _round_qty(self, val):
        digits = self.env['sale.discount.rule']._fields['min_qty'].digits[1]
        return round(val, digits)

    def _get_excluded_products(self):
        products = self.excluded_product_ids

        def get_children_recursive(categ):
            res = categ
            for child in categ.child_id:
                res += get_children_recursive(child)
            return res

        categs = self.env['product.category']
        for categ in self.excluded_product_category_ids:
            categs += get_children_recursive(categ)
        products += self.env['product.product'].search(
            [('categ_id', 'in', categs._ids)])

        return products
