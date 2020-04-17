# Copyright (C) 2015 ICTSTUDIO (<http://www.ictstudio.eu>).
# Copyright (C) 2016-2020 Noviat nv/sa (www.noviat.com).
# Copyright (C) 2016 Onestein (http://www.onestein.eu/).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleDiscountRule(models.Model):
    _name = "sale.discount.rule"
    _description = "Sale Order Discount Rule"
    _order = "sequence"

    sale_discount_id = fields.Many2one(
        comodel_name="sale.discount", string="Sale Discount", required=True
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.user.company_id,
    )
    sequence = fields.Integer(default=10)
    discount_base = fields.Selection(
        related="sale_discount_id.discount_base", readonly=True
    )
    # matching criteria
    matching_type = fields.Selection(
        selection="_selection_matching_type",
        default="amount",
        required=True,
        help="Select if the discount will be granted based upon "
        "value or quantity of goods sold ",
    )
    matching_extra = fields.Selection(
        selection="_selection_matching_extra",
        string="Extra condition",
        required=True,
        default="none",
        help="This field will result on extra constraints to determine "
        "a matching rule. These constraints may vary per country",
    )
    product_ids = fields.Many2many(
        comodel_name="product.product",
        relation="product_product_sale_discount_rule_rel",
        string="Products",
    )
    product_category_ids = fields.Many2many(
        comodel_name="product.category",
        relation="product_category_sale_discount_rule_rel",
        string="Product Categories",
    )
    min_base = fields.Float(string="Minimum Base Amount", digits=("Product Price"))
    max_base = fields.Float(string="Maximum Base Amount", digits=("Product Price"))
    min_qty = fields.Float(
        string="Minimum Quantity", digits=("Product Unit of Measure")
    )
    max_qty = fields.Float(
        string="Maximum Quantity", digits=("Product Unit of Measure")
    )
    # the *_view fields are only used for tree view
    # readabily purposes. All calculations are based upon the
    # min/max_* fields.
    min_view = fields.Float(
        string="Minimum",
        digits=("Product Unit of Measure"),
        compute="_compute_min_view",
    )
    max_view = fields.Float(
        string="Maximum",
        digits=("Product Unit of Measure"),
        compute="_compute_max_view",
    )
    product_view = fields.Char(
        string="Product / Product Category", compute="_compute_product_view"
    )
    # results
    discount_type = fields.Selection(
        selection=[("perc", "Percentage"), ("amnt", "Amount")],
        default="perc",
        required=True,
        help="Select if the granted discount will be "
        "a percentage of the value of goods sold "
        "or a fixed amount ",
    )
    discount_pct = fields.Float(string="Discount Percentage", digits="Discount")
    discount_amount = fields.Float(string="Discount Amount", digits=("Product Price"))
    discount_amount_invisible = fields.Boolean(
        compute="_compute_discount_fields_invisible"
    )
    discount_amount_unit = fields.Float(
        string="Discount Amount per Unit", digits=("Product Price")
    )
    discount_amount_unit_invisible = fields.Boolean(
        compute="_compute_discount_fields_invisible"
    )
    discount_view = fields.Float(
        string="Discount", digits=("Discount"), compute="_compute_discount_view"
    )

    @api.model
    def _selection_matching_type(self):
        return [("amount", "Amount"), ("quantity", "Quantity")]

    @api.model
    def _selection_matching_extra(self):
        return [("none", "None")]

    @api.depends("min_base", "min_qty")
    def _compute_min_view(self):
        for rule in self:
            rule.min_view = (
                rule.matching_type == "amount" and rule.min_base or rule.min_qty
            )

    @api.depends("max_base", "max_qty")
    def _compute_max_view(self):
        for rule in self:
            rule.max_view = (
                rule.matching_type == "amount" and rule.max_base or rule.max_qty
            )

    @api.depends("discount_base")
    def _compute_product_view(self):
        for rule in self:
            rule.product_view = (
                rule.product_ids
                and ", ".join(rule.product_ids.mapped("display_name"))
                or ", ".join(rule.product_category_ids.mapped("display_name"))
                or ""
            )

    @api.depends("discount_pct", "discount_amount", "discount_amount_unit")
    def _compute_discount_view(self):
        for rule in self:
            if (
                rule.discount_base == "sale_line"
                and rule.matching_type == "quantity"
                and rule.discount_type == "amnt"
            ):
                if len(rule.product_ids) == 1:
                    rule.discount_view = rule.discount_amount_unit
                else:
                    rule.discount_view = rule.discount_amount
            else:
                if rule.discount_type == "perc":
                    rule.discount_view = rule.discount_pct
                elif rule.discount_type == "amnt":
                    rule.discount_view = rule.discount_amount
                else:
                    raise NotImplementedError

    @api.depends("discount_base", "discount_type", "matching_type", "product_ids")
    def _compute_discount_fields_invisible(self):
        self._onchange_discount_fields_invisible()

    @api.onchange("discount_base", "discount_type", "matching_type", "product_ids")
    def _onchange_discount_fields_invisible(self):
        for rule in self:
            if rule.discount_type == "perc":
                rule.discount_amount_invisible = True
                rule.discount_amount_unit_invisible = True
            else:
                if rule.discount_base == "sale_line":
                    if rule.matching_type == "quantity":
                        if len(rule.product_ids) == 1:
                            rule.discount_amount_invisible = True
                        else:
                            rule.discount_amount_invisible = False
                            rule.discount_amount_unit_invisible = True
                    else:
                        # matching_type == 'amount'
                        rule.discount_amount_invisible = False
                        rule.discount_amount_unit_invisible = True
                else:
                    # discount_base == 'sale_order'
                    rule.discount_amount_invisible = False
                    rule.discount_amount_unit_invisible = True

    @api.constrains(
        "discount_pct", "discount_amount", "discount_amount_unit", "discount_type"
    )
    def _check_sale_discount(self):
        """
        By default only discounts are supported, but you can
        adapt this method to allow also price increases.
        """
        # Check if amount is positive
        if self.discount_type == "amnt" and (
            self.discount_amount < 0 or self.discount_amount_unit < 0
        ):
            raise ValidationError(_("Discount Amount needs to be a positive number"))
        # Check if percentage is between 0 and 100
        elif self.discount_type == "perc" and (
            self.discount_pct < 0 or self.discount_pct > 100
        ):
            raise ValidationError(_("Percentage discount must be between 0 and 100."))

    @api.constrains("product_ids", "product_category_ids")
    def _check_product_filters(self):
        if self.product_ids and self.product_category_ids:
            raise ValidationError(
                _("Products and Product Categories are mutually exclusive")
            )

    @api.constrains("min_base", "max_base")
    def _check_min_max_base(self):
        if self.min_base and self.max_base:
            if self.max_base < self.min_base:
                raise ValidationError(
                    _(
                        "The 'Maximum Base Amount' may not be lower "
                        "than the 'Minimum Base Amount'."
                    )
                )

    @api.constrains("min_qty", "max_qty")
    def _check_min_max_qty(self):
        if self.min_qty and self.max_qty:
            if self.max_qty < self.min_qty:
                raise ValidationError(
                    _(
                        "The 'Maximum Quantity' may not be lower "
                        "than the 'Minimum Quantity'."
                    )
                )

    @api.onchange("matching_type")
    def _onchange_matching_type(self):
        if self.matching_type == "quantity":
            self.product_category_ids = False

    @api.onchange("product_ids")
    def _onchange_product_ids(self):
        if self.product_ids:
            self.product_category_ids = False

    @api.onchange("product_category_ids")
    def _onchange_product_category_ids(self):
        if self.product_category_ids:
            self.product_ids = False

    def _matching_type_methods(self):
        """
        Extend this dictionary in order to add methods to support
        custom matching_types.
        Such a method should return True (match) of False (no match).
        """
        return {}

    def _matching_extra_methods(self):
        """
        Extend this dictionary in order to add support
        for matching_extra methods.
        Such a method should return True (match) of False (no match).
        """
        return {}
