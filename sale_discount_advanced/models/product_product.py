# See LICENSE file for full copyright and licensing details.

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _belongs_to_category(self, category):
        """
        Returns True if the product category or one of its children
        is equal to 'category'.
        """
        self.ensure_one()

        def check_category_recursive(product, category):
            if product.categ_id == category:
                return True
            else:
                for categ in category.child_id:
                    check = check_category_recursive(product, categ)
                    if check:
                        return True
                return False

        return check_category_recursive(self, category)
