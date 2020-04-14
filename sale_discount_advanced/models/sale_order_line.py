# Copyright (C) 2015 ICTSTUDIO (<http://www.ictstudio.eu>).
# Copyright (C) 2016-2019 Noviat nv/sa (www.noviat.com).
# Copyright (C) 2016 Onestein (http://www.onestein.eu/).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openerp import api, fields, models

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    sale_discount_ids = fields.Many2many(
        comodel_name="sale.discount",
        relation="sale_line_sale_discount_rel",
        column1="sale_line_id",
        column2="discount_id",
        string="Discount Engine(s)",
        help="Discount engines used for sale order line " "discount calculation.",
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

    def product_id_change(
        self,
        cr,
        uid,
        ids,
        pricelist_id,
        product_id,
        qty=0,
        uom=False,
        qty_uos=0,
        uos=False,
        name="",
        partner_id=False,
        lang=False,
        update_tax=True,
        date_order=False,
        packaging=False,
        fiscal_position=False,
        flag=False,
        context=None,
    ):
        res = super(SaleOrderLine, self).product_id_change(
            cr,
            uid,
            ids,
            pricelist_id,
            product_id,
            qty=qty,
            uom=uom,
            qty_uos=qty_uos,
            uos=uos,
            name=name,
            partner_id=partner_id,
            lang=lang,
            update_tax=update_tax,
            date_order=date_order,
            packaging=packaging,
            fiscal_position=fiscal_position,
            flag=flag,
            context=context,
        )
        disc_ids = self._get_sale_discount_ids(
            cr, uid, product_id, date_order, context=context
        )
        res["value"].update(sale_discount_ids=[(6, 0, disc_ids)])
        return res

    def _get_sale_discount_ids(self, cr, uid, product_id, date_order, context=None):
        """
        v7 api.
        By default sale order lines without products are not
        included in the discount calculation.
        You can still add a discount manually to such a line or
        add non-product lines via an inherit on this method.
        """
        if not product_id:
            return []
        if context is None:
            context = {}
        discount_ctx = context.get("discount_ids")
        if not discount_ctx:
            return []
        discount_ids = discount_ctx[0][2]
        self.env = api.Environment(cr, uid, context)
        discounts = self.env["sale.discount"]
        so_discounts = self.env["sale.discount"].browse(discount_ids)
        product = self.env["product.product"].browse(product_id)
        for discount in so_discounts:
            if discount._check_product_filter(product) and discount._check_active_date(
                check_date=date_order
            ):
                discounts += discount
        return discounts.ids

    def _get_sale_discounts(self):
        """
        v8 api.
        By default sale order lines without products are not
        included in the discount calculation.
        You can still add a discount manually to such a line or
        add non-product lines via an inherit on this method.
        """
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
