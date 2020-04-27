# Copyright 2019 Noviat.
# Copyright (C) 2020-TODAY SerpentCS Pvt. Ltd. (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderGroupAddOrder(models.TransientModel):
    _name = "sale.order.group.add.order"
    _description = "Add orders to Sale Order Group"

    sale_order_group_id = fields.Many2one(
        comodel_name="sale.order.group", string="Sale Order Group", readonly=True
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        related="sale_order_group_id.partner_id",
        string="Partner",
        readonly=True,
    )
    sale_order_ids = fields.Many2many(comodel_name="sale.order", string="Orders")

    @api.onchange("sale_order_group_id")
    def _onchange_sale_order_group_id(self):
        so_dom = self._get_so_dom()
        return {"domain": {"sale_order_ids": so_dom}}

    def _get_so_dom(self):
        return [
            ("state", "in", ["draft", "sent"]),
            ("sale_order_group_id", "=", False),
            ("partner_id.commercial_partner_id", "=", self.partner_id.id),
        ]

    def add_to_group(self):
        self.ensure_one()
        self.sale_order_ids.write({"sale_order_group_id": self.sale_order_group_id.id})
        return True
