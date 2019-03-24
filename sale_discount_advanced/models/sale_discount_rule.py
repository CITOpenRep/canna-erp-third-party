# -*- coding: utf-8 -*-
# Copyright (C) 2015 ICTSTUDIO (<http://www.ictstudio.eu>).
# Copyright (C) 2016-2019 Noviat nv/sa (www.noviat.com).
# Copyright (C) 2016 Onestein (http://www.onestein.eu/).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openerp import api, fields, models, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SaleDiscountRule(models.Model):
    _name = 'sale.discount.rule'
    _order = 'sequence'

    sale_discount_id = fields.Many2one(
        comodel_name='sale.discount',
        string='Sale Discount',
        required=True)
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.user.company_id)
    sequence = fields.Integer(default=10)
    discount_base = fields.Selection(
        related='sale_discount_id.discount_base', readonly=True)
    # matching criteria
    matching_type = fields.Selection(
        selection=[
            ('amount', 'Amount'),
            ('quantity', 'Quantity')],
        default='amount',
        required=True,
        help="Select if the discount will be granted based upon "
             "value or quantity of goods sold ")
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product')
    product_category_id = fields.Many2one(
        comodel_name='product.category',
        string='Product Category')
    min_base = fields.Float(
        string='Minimum base amount',
        digits=dp.get_precision('Account'))
    max_base = fields.Float(
        string='Maximum base amount',
        digits=dp.get_precision('Account'))
    min_qty = fields.Float(
        string='Minimum quantity',
        digits=dp.get_precision('Product UoS'))
    max_qty = fields.Float(
        string='Maximum quantity',
        digits=dp.get_precision('Product UoS'))
    # the *_view fields are only used for tree view
    # readabily purposes. All calculations are based upon the
    # min/max_* fields.
    min_view = fields.Float(
        string='Minimum',
        digits=dp.get_precision('Product UoS'),
        compute='_compute_min_view')
    max_view = fields.Float(
        string='Maximum',
        digits=dp.get_precision('Product UoS'),
        compute='_compute_max_view')
    product_view = fields.Char(
        string='Product / Product Category',
        compute='_compute_product_view')
    # results
    discount_type = fields.Selection(
        selection=[
            ('perc', 'Percentage'),
            ('amnt', 'Amount')],
        default='perc',
        required=True,
        help="Select if the granted discount will be "
             "a percentage of the value of goods sold "
             "or a fixed amount ")
    discount_pct = fields.Float(
        string="Discount Percentage")
    discount_amount = fields.Float(
        string="Discount Amount",
        digits=dp.get_precision('Account'))
    discount_amount_invisible = fields.Boolean(
        compute='_compute_discount_fields_invisible')
    discount_amount_unit = fields.Float(
        string="Discount Amount per Unit",
        digits=dp.get_precision('Account'))
    discount_amount_unit_invisible = fields.Boolean(
        compute='_compute_discount_fields_invisible')
    discount_view = fields.Float(
        string='Discount',
        digits=dp.get_precision('Account'),
        compute='_compute_discount_view')

    @api.depends('min_base', 'min_qty')
    def _compute_min_view(self):
        for rule in self:
            rule.min_view = rule.matching_type == 'amount' and \
                rule.min_base or rule.min_qty

    @api.depends('max_base', 'max_qty')
    def _compute_max_view(self):
        for rule in self:
            rule.max_view = rule.matching_type == 'amount'and \
                rule.max_base or rule.max_qty

    @api.depends('discount_base')
    def _compute_product_view(self):
        for rule in self:
            if rule.discount_base == "sale_order":
                rule.product_view = 'n/a'
            else:
                rule.product_view = (
                    rule.product_id.display_name or
                    rule.product_category_id.display_name or '')

    @api.depends('discount_pct', 'discount_amount', 'discount_amount_unit')
    def _compute_discount_view(self):
        for rule in self:
            if (rule.discount_base == 'sale_line' and
                    rule.matching_type == 'quantity' and
                    rule.discount_type == 'amnt'):
                if rule.product_id:
                    rule.discount_view = rule.discount_amount_unit
                else:
                    rule.discount_view = rule.discount_amount
            else:
                if rule.discount_type == 'perc':
                    rule.discount_view = rule.discount_pct
                elif rule.discount_type == 'amnt':
                    rule.discount_view = rule.discount_amount
                else:
                    raise NotImplementedError

    @api.depends('discount_base', 'discount_type', 'matching_type',
                 'product_id')
    def _compute_discount_fields_invisible(self):
        for rule in self:
            if rule.discount_type == 'perc':
                rule.discount_amount_invisible = True
                rule.discount_amount_unit_invisible = True
            else:
                if rule.discount_base == 'sale_line':
                    if rule.matching_type == 'quantity':
                        if rule.product_id:
                            rule.discount_amount_invisible = True
                        else:
                            rule.discount_amount_unit_invisible = True
                    else:
                        # matching_type == 'amount'
                        rule.discount_amount_unit_invisible = True
                else:
                    # discount_base == 'sale_order'
                    rule.discount_amount_unit_invisible = True

    @api.one
    @api.constrains('discount_pct', 'discount_amount',
                    'discount_amount_unit', 'discount_type')
    def _check_sale_discount(self):
        """
        By default only discounts are supported, but you can
        adapt this method to allow also price increases.
        """
        # Check if amount is positive
        if self.discount_view < 0:
            raise ValidationError(_(
                "Discount Amount needs to be a positive number"))
        # Check if percentage is between 0 and 100
        elif self.discount_type == 'perc' and self.discount_view > 100:
            raise ValidationError(_(
                "Percentage discount must be between 0 and 100."))

    @api.onchange('matching_type')
    def _onchange_matching_type(self):
        if self.matching_type == 'quantity':
            self.product_category_id = False

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.product_category_id = False

    @api.onchange('product_category_id')
    def _onchange_product_category_id(self):
        if self.product_category_id:
            self.product_id = False
