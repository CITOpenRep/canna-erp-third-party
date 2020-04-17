# Copyright (C) 2015 ICTSTUDIO (<http://www.ictstudio.eu>).
# Copyright (C) 2016-2020 Noviat nv/sa (www.noviat.com).
# Copyright (C) 2016 Onestein (http://www.onestein.eu/).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    sale_discount_ids = fields.Many2many(
        comodel_name="sale.discount",
        relation="sale_line_sale_discount_rel",
        column1="sale_line_id",
        column2="discount_id",
        string="Discount Engine(s)",
        help="Discount engines used for sale order line discount calculation.",
    )
    applied_sale_discount_ids = fields.Many2many(
        comodel_name="sale.discount",
        relation="sale_line_applied_sale_discount_rel",
        column1="sale_line_id",
        column2="discount_id",
        string="Discount Engine(s)",
        readonly=True,
        help="This field contains the subset of the discount enginges "
        "with a calculated discount amount > 0.",
    )

    @api.model
    def _prepare_add_missing_fields(self, vals):
        """
        The order_id.discount_ids are still empty when creating order and order_line
        via one single create command containing both the order and order_line fields.
        As a consequence the 'product_id_change' will not find the SO discount_ids
        and hence also not set the correct sale_discount_ids on the order lines.
        We bypass this ORM limitation setting the so_discount_ids when passed
        via the context.
        """
        res = super()._prepare_add_missing_fields(vals)
        discount_ctx = self.env.context.get("so_discount_ids")
        if (
            "sale_discount_ids" in vals
            or not discount_ctx
            or not vals.get("order_id")
            or not vals.get("product_id")
        ):
            return res

        so = self.order_id.browse(vals["order_id"])
        if not so.discount_ids:
            so.discount_ids = self.env["sale.discount"].browse(discount_ctx[0][2])
        line = self.new(vals)
        # We execute again the product_id_change (already done in super).
        # This code is not optimal but Odoo has not designed this method to
        # extend the 'onchange_fields' via inherit and we prefer not
        # to break the inheritance chain to allow other community modules
        # to add more fields.
        line.product_id_change()
        field = "sale_discount_ids"
        res[field] = line._fields[field].convert_to_write(line[field], line)
        return res

    @api.onchange("product_id")
    def product_id_change(self):
        res = super().product_id_change()
        if self.product_id:
            self.sale_discount_ids = self._get_sale_discounts()
        return res

    def _get_sale_discounts(self):
        self.ensure_one()
        discounts = self.env["sale.discount"]
        if not self.product_id:
            return discounts
        date_order = self.order_id.date_order
        for discount in self.order_id.discount_ids:
            if discount._check_product_filter(
                self.product_id
            ) and discount._check_active_date(check_date=date_order):
                discounts += discount
        return discounts
