# -*- coding: utf-8 -*-
# Copyright (C) 2016-2019 Noviat nv/sa (www.noviat.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class SaleDiscount(models.Model):
    _inherit = 'sale.discount'

    payment_term_ids = fields.Many2many(
        comodel_name='account.payment.term',
        relation='payterm_sale_discount_rel',
        column1='discount_id',
        column2='payterm_id',
        readonly=True)
