# -*- coding: utf-8 -*-
# Copyright (C) 2015 ICTSTUDIO (<http://www.ictstudio.eu>).
# Copyright (C) 2012-2016 Noviat nv/sa (www.noviat.com).
# Copyright (C) 2016 Onestein (http://www.onestein.eu).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import api, fields, models


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    sale_discount_ids = fields.Many2many(
        string='Sale Discounts',
        comodel_name='sale.discount',
        relation='pricelist_sale_discount_rel',
        column1='pricelist_id',
        column2='discount_id')

    @api.multi
    def _get_active_sale_discounts(self, date_order):
        self.ensure_one()
        discounts = self.env['sale.discount']
        for discount in self.sale_discount_ids:
            if discount.active and \
                    discount.check_active_date(date_order):
                discounts += discount
        return discounts
