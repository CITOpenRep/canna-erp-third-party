# Copyright 2019 Noviat.
# Copyright (C) 2020-TODAY SerpentCS Pvt. Ltd. (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrderGroup(models.Model):
    _inherit = "sale.order.group"

    # discount_ids currently computed field, hence discount
    # changes must be set on the underlying Sale Orders
    discount_ids = fields.Many2many(
        string="Sale Discount engines",
        comodel_name="sale.discount",
        relation="sale_order_group_discount_rel",
        column1="so_group_id",
        column2="discount_id",
        compute="_compute_discounts",
        store=True,
        help="Sale Discount engines for this Sale Order Group.",
    )
    disable_discount_calc = fields.Boolean(
        compute="_compute_discounts",
        help="Do not allow discount calculation on the combined order value "
        "when the underlying orders have different discount settings.",
    )

    @api.depends("sale_order_ids.discount_ids")
    def _compute_discounts(self):
        for sog in self:
            orders = sog.sale_order_ids.filtered(lambda x: x.state in ["draft", "sent"])
            if orders:
                sog.discount_ids = orders[0].discount_ids
                sog.disable_discount_calc = False
                for order in orders[1:]:
                    if order.discount_ids != sog.discount_ids:
                        sog.disable_discount_calc = True
                        sog.discount_ids = False
                        continue

    @api.constrains("sale_order_ids")
    def _check_sale_order_ids(self):
        for group in self:
            if len(group.sale_order_ids.mapped("currency_id")) > 1:
                raise UserError(
                    _(
                        "The selected orders have different currencies. "
                        "Such orders cannot be grouped together."
                    )
                )

    def calculate_discount(self):
        self.ensure_one()
        self._calculate_discount_checks()
        orders = self.sale_order_ids.filtered(lambda x: x.state in ["draft", "sent"])
        orders.compute_discount()
        return True

    def _calculate_discount_checks(self):
        if self.disable_discount_calc:
            raise UserError(_("Operation not allowed."))
        if self.state != "draft":
            raise UserError(_("Operation not allowed."))

    def button_confirm(self):
        """
        Bypass discount recalc per individual order.
        """
        ctx = dict(self.env.context, skip_discount_calc=True)
        return super(SaleOrderGroup, self.with_context(ctx)).button_confirm()
