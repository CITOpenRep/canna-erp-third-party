# -*- coding: utf-8 -*-
# Copyright (C) 2015 ICTSTUDIO (<http://www.ictstudio.eu>).
# Copyright (C) 2016-2019 Noviat nv/sa (www.noviat.com).
# Copyright (C) 2016 Onestein (http://www.onestein.eu/).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta
import logging

from openerp import api, fields, models, _
from openerp.exceptions import ValidationError, Warning as UserError

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
        default='sale_order_group',
        track_visibility='onchange',
        help="Base the discount on ")
    exclusive = fields.Selection(
        selection=[('always', 'Always'),
                   ('highest', 'Use Highest')],
        string='Exclusive',
        help="This discount engine will be used exclusively for the "
             "sale order line discount calculation "
             "if a rule of this engine matches for the line."
             "\nThe order of the discount object will determine which one of "
             "the 'exclusive' discount engines will be selected "
             "in case multiple 'exclusive' discount objects have been set "
             "on this sales order (the order is set via the discount "
             "'sequence' field, the lowest sequence will be selected)."
             "\nThe 'Use Highest' option will change this behaviour: "
             "when the granted exclusive discount is lower than the sum of "
             "the discounts calculated by the other discount engines "
             "than the exclusive discount will be dropped "
             "in favour of the other engines."
    )
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
            ('sale_order_group', 'Base discount on group of orders'),
            ('sale_line', 'Base discount on order line'),
        ]
        return selection

    @api.onchange('discount_base')
    def _onchange_discount_base(self):
        self.rule_ids.write({
            'matching_type': 'amount',
            'product_id': False,
            'exclusive': False,
            'product_category_ids': [(5, )],
            'discount_type': 'perc',
            'discount_pct': 0.0,
            'discount_amount': 0.0,
            'discount_amount_unit': 0.0,
        })

    @api.one
    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValidationError(
                    _("The end date may not be lower than the start date."))

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

    def _check_active_date(self, check_date=None):
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

    def _calculate_discount(self, lines):

        for rule in self.rule_ids:
            disc_amt = 0.0
            disc_pct = 0.0
            qty = 0.0
            base = 0.0
            for sol in lines:
                if rule.product_ids:
                    if sol.product_id not in rule.product_ids:
                        continue
                elif rule.product_category_ids:
                    if not any(sol.product_id._belongs_to_category(categ)
                               for categ in rule.product_category_ids):
                        continue
                qty += sol.product_uom_qty
                base += sol.product_uom_qty * sol.price_unit

            match = False
            if rule.matching_type == 'amount':
                match_min = match_max = False
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
                match = match_min and match_max
            elif rule.matching_type == 'quantity':
                match_min = match_max = False
                qty = sum([x.product_uom_qty for x in lines])
                qty = self._round_qty(qty)
                rule_min_qty = self._round_qty(rule.min_qty)
                rule_max_qty = self._round_qty(rule.max_qty)
                if rule_min_qty > 0 and rule_min_qty > qty:
                    continue
                else:
                    match_min = True
                if rule_max_qty > 0 and rule_max_qty < qty:
                    continue
                else:
                    match_max = True
                match = match_min and match_max
            else:
                method = rule._matching_type_methods().get(
                    rule.matching_type)
                if not method:
                    raise UserError(_(
                        "Programming error: no method defined for "
                        "matching_type '%s'."
                    ) % rule.matching_type)
                match = getattr(rule, method)(lines)

            if match:
                if rule.matching_extra != 'none':
                    method = rule._matching_extra_methods().get(
                        rule.matching_extra)
                    if not method:
                        raise UserError(_(
                            "Programming error: no method defined for "
                            "matching_extra '%s'."
                        ) % rule.matching_extra)
                    if not getattr(rule, method)(lines):
                        # The extra matching condition is only applied if all
                        # other conditions match. If the extra matching
                        # condition returns False, then do not apply this rule.
                        break
                if rule.discount_type == 'perc':
                    disc_amt = base * rule.discount_pct / 100.0
                    disc_pct = rule.discount_pct
                else:
                    if rule.matching_type == 'quantity' and \
                            len(rule.product_ids) == 1:
                        disc_amt = min(
                            rule.discount_amount_unit * qty, base)
                    else:
                        disc_amt = min(rule.discount_amount, base)
                    disc_pct = disc_amt / base * 100.0
                # Do not apply any other rules for this discount.
                break

        return match, disc_pct

    def _round_amt(self, val):
        digits = self.env['sale.discount.rule']._fields['min_base'].digits[1]
        return round(val, digits)

    def _round_qty(self, val):
        digits = self.env['sale.discount.rule']._fields['min_qty'].digits[1]
        return round(val, digits)

    def _check_product_filter(self, product):
        """
        Checks if the discount object applies to the given product
        """
        self.ensure_one()
        if self._is_excluded_product(product):
            return False
        else:
            filter = self.included_product_ids or \
                self.included_product_category_ids
            if filter:
                return self._is_included_product(product) and True or False
        return True

    def _is_excluded_product(self, product):
        self.ensure_one()
        c1 = product in self.excluded_product_ids
        c2 = False
        for categ in self.excluded_product_category_ids:
            if product._belongs_to_category(categ):
                c2 = True
                break
        return c1 or c2

    def _is_included_product(self, product):
        self.ensure_one()
        c1 = product in self.included_product_ids
        c2 = False
        for categ in self.included_product_category_ids:
            if product._belongs_to_category(categ):
                c2 = True
                break
        return c1 or c2
