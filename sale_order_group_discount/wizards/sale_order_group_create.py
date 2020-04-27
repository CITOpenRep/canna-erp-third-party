# Copyright 2019 Noviat.
# Copyright (C) 2020-TODAY SerpentCS Pvt. Ltd. (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, models


class SaleOrderGroupCreate(models.TransientModel):
    _inherit = "sale.order.group.create"

    @api.model
    def default_get(self, fields_list):
        res = super(SaleOrderGroupCreate, self).default_get(fields_list)
        orders = self.env["sale.order"].browse(self.env.context.get("active_ids"))
        discounts = orders[0].discount_ids
        currency = orders[0].currency_id
        for order in orders[1:]:
            if order.discount_ids != discounts:
                msg = "\n\n" + _("Warning:") + "\n"
                msg += _(
                    "The selected orders have different discounts. "
                    "Align these discounts first if you want to apply "
                    "the discount calculation on the combined set of orders."
                )
                res["note"] += msg
                break
            if order.currency_id != currency:
                msg = "\n\n" + _("Warning:") + "\n"
                msg += _(
                    "The selected orders have different currencies. "
                    "Such orders cannot be grouped together."
                )
                res["note"] += msg
                break
        return res

    def _prepare_sale_order_group_vals(self):
        """
        Add discounts to vals only if all grouped orders have the
        same discounts.
        """
        vals = super(SaleOrderGroupCreate, self)._prepare_sale_order_group_vals()
        orders = self.env["sale.order"].browse(self.env.context.get("active_ids"))
        discounts = orders[0].discount_ids
        for order in orders[1:]:
            if order.discount_ids != discounts:
                return vals
        vals["discount_ids"] = [(6, 0, discounts.ids)]
        return vals
