# Copyright 2019 Onestein (https://www.onestein.nl/).
# Copyright 2020 Noviat (www.noviat.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleDiscountRule(models.Model):
    _inherit = "sale.discount.rule"

    min_pallet = fields.Float(string="Minimum number of pallets")
    max_pallet = fields.Float(string="Maximum number of pallets")

    @api.model
    def _selection_matching_type(self):
        res = super()._selection_matching_type()
        return res + [("pallet", "Pallet")]

    def _matching_type_methods(self):
        methods = super()._matching_type_methods()
        methods["pallet"] = "_pallet_matching"
        return methods

    def _compute_pallets(self, lines):
        pallets = 0
        for line in lines:
            packaging = line.product_id.packaging_ids.filtered(
                lambda r: r.packaging_type_id.is_pallet
            )
            if not packaging:
                continue
            if len(packaging) > 1:
                raise NotImplementedError(
                    "Product {} (id: {}) has more than one packaging "
                    "configuration of type pallet.".format(
                        line.product_tmpl_id.name, line.product_tmpl_id.id
                    )
                )
            pallets += line.product_uom_qty / (packaging.qty or 1)
        return pallets

    def _pallet_matching(self, lines):
        self.ensure_one()
        pallet_lines = self.env["sale.order.line"]
        for sol in lines:
            if self.product_ids:
                if sol.product_id not in self.product_ids:
                    continue
            elif self.product_category_ids:
                if not any(
                    sol.product_id._belongs_to_category(categ)
                    for categ in self.product_category_ids
                ):
                    continue
            pallet_lines += sol
        computed_pallets = self._compute_pallets(pallet_lines)
        if self.min_pallet > 0 and self.min_pallet > computed_pallets:
            return False
        if self.max_pallet > 0 and self.max_pallet < computed_pallets:
            return False
        return True

    @api.onchange("matching_type")
    def _onchange_matching_type(self):
        if self.matching_type == "pallet":
            self.product_category_ids = False
        super()._onchange_matching_type()

    @api.depends("min_base", "min_qty", "min_pallet")
    def _compute_min_view(self):
        for rule in self:
            if rule.matching_type == "pallet":
                rule.min_view = rule.min_pallet
            else:
                super(SaleDiscountRule, rule)._compute_min_view()

    @api.depends("max_base", "max_qty", "max_pallet")
    def _compute_max_view(self):
        for rule in self:
            if rule.matching_type == "pallet":
                rule.max_view = rule.max_pallet
            else:
                super(SaleDiscountRule, rule)._compute_max_view()
