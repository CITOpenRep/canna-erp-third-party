# -*- coding: utf-8 -*-
# Copyright (C) 2015 ICTSTUDIO (<http://www.ictstudio.eu>).
# Copyright (C) 2016-2019 Noviat nv/sa (www.noviat.com).
# Copyright (C) 2016 Onestein (http://www.onestein.eu/).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta
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
    included_product_category_ids = fields.Many2many(
        comodel_name='product.category',
        relation='product_category_sale_discount_incl_rel',
        string='Included Product Categories',
        track_visibility='onchange',
        help="Fill in this field to limit the discount calculation "
             "to Products in these categories.")
    included_product_ids = fields.Many2many(
        comodel_name='product.product',
        relation='product_sale_discount_incl_rel',
        string='Included Products',
        track_visibility='onchange',
        help="Fill in this field to limit the discount calculation "
             "to these products.")

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
            ('sale_order', 'Base discount on order'),
            ('sale_line', 'Base discount on order line'),
        ]
        return selection

    @api.onchange('discount_base')
    def _onchange_discount_base(self):
        self.rule_ids.write({'matching_type': 'amount'})

    @api.one
    @api.constrains('rule_ids')
    def _check_overlaps(self):
        rulesets = []
        if self.discount_base == 'sale_order':
            ruleset = self.rule_ids.sorted(key=lambda r: r.min_view)
            if ruleset:
                rulesets.append((ruleset, 'amount'))
        else:
            products = self.rule_ids.mapped('product_id')
            for matching_type in ('amount', 'quantity'):
                for product in products:
                    ruleset = self.rule_ids.filtered(
                        lambda r: r.matching_type == matching_type and
                        r.product_id == product)
                    if ruleset:
                        ruleset = ruleset.sorted(
                            key=lambda r: r.min_view)
                        rulesets.append((ruleset, matching_type))
        for ruleset in rulesets:
            stack = []
            overlap = False
            if ruleset[1] == 'amount':
                fld_min = 'min_base'
                fld_max = 'max_base'
            else:
                fld_min = 'min_qty'
                fld_max = 'max_qty'
            for i, rule in enumerate(ruleset[0], start=1):
                min = getattr(rule, fld_min) or 0.0
                max = getattr(rule, fld_max) or float('inf')
                if stack:
                    previous = stack.pop()
                    if min == previous[2]:
                        overlap = True
                        break
                    if min <= previous[3]:
                        overlap = True
                        break
                else:
                    stack.append((i, rule, min, max))
            if overlap:
                raise UserError(_(
                    "Rule %s overlaps with rule %s") % (previous[0], i))

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
        end_date = self.end_date
        if end_date:
            end_date = (
                datetime.strptime(end_date, '%Y-%m-%d') +
                timedelta(days=1)
            ).strftime('%Y-%m-%d')
        if self.start_date and end_date \
                and (check_date >= self.start_date and
                     check_date < end_date):
            return True
        if self.start_date and not end_date \
                and (check_date >= self.start_date):
            return True
        if not self.start_date and self.end_date \
                and (check_date < end_date):
            return True
        elif not self.start_date or not end_date:
            return True
        else:
            return False

    def _calculate_line_discount(self, line):
        return self._calculate_discount(line.price_unit, line=line)

    def _calculate_discount(self, price_unit, lines=None, line=None):
        if not lines:
            if not line:
                raise NotImplementedError
            qty = line.product_uom_qty
        else:
            qty = 1.0
        base = qty * price_unit
        disc_amt = 0.0
        disc_pct = 0.0
        for rule in self.rule_ids:
            if (line and rule.product_id and
                    line.product_id != rule.product_id):
                continue
            if line and rule.product_category_id:
                rule_categs = self.env['product.category'].search(
                    [('child_id', 'child_of', rule.product_category_id.id)])
                if line.product_id.categ_id not in rule_categs:
                    continue
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
                if lines:
                    # discount_base == sale_order
                    qty = sum([x[0].product_uom_qty for x in lines])
                qty = self._round_qty(qty)
                rule_min_qty = self._round_qty(rule.min_qty)
                rule_max_qty = self._round_qty(rule.max_qty)
                if line and line.product_id == rule.product_id or lines:
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

    def _get_included_products(self):
        products = self.included_product_ids

        def get_children_recursive(categ):
            res = categ
            for child in categ.child_id:
                res += get_children_recursive(child)
            return res

        categs = self.env['product.category']
        for categ in self.included_product_category_ids:
            categs += get_children_recursive(categ)
        products += self.env['product.product'].search(
            [('categ_id', 'in', categs._ids)])

        return products
