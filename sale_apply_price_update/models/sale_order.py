# Copyright 2020 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def button_update_prices(self):
        digits = self.env['decimal.precision'].precision_get('Product Price')
        for so in self:
            for sol in so.order_line:
                product = sol.product_id
                display_price = sol._get_display_price(product)
                price_unit = self.env['account.tax']._fix_tax_included_price_company(
                    display_price, product.taxes_id, sol.tax_id, sol.company_id)
                if round(price_unit - sol.price_unit, digits):
                    sol.price_unit = price_unit
        return True
