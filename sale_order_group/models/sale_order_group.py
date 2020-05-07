# Copyright 2019 Noviat.
# Copyright (C) 2020-TODAY SerpentCS Pvt. Ltd. (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class SaleOrderGroup(models.Model):
    _name = "sale.order.group"
    _description = "Sale Order Group"

    name = fields.Char(
        string="Order Group Reference",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: self._default_name(),
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("confirm", "Confirmed"),
            ("cancel", "Cancelled"),
        ],
        readonly=True,
        default="draft",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner", string="Partner", readonly=True
    )
    sale_order_ids = fields.One2many(
        comodel_name="sale.order",
        inverse_name="sale_order_group_id",
        string="Orders",
        copy=False,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        readonly=True,
        default=lambda self: self.env.user.company_id,
    )

    @api.model
    def _default_name(self):
        return self.env["ir.sequence"].next_by_code("sale.order.group")

    def button_confirm(self):
        ctx = dict(self.env.context, confirm_from_group=True)
        for so in self.sale_order_ids.with_context(ctx):
            so.action_confirm()
        self.state = "confirm"
        return True

    def button_cancel(self):
        ctx = dict(self.env.context, cancel_from_group=True)
        res = self.sale_order_ids.with_context(ctx).action_cancel()
        self.state = "cancel"
        return res

    def add_orders(self):
        self.ensure_one()
        ctx = dict(self.env.context, default_sale_order_group_id=self.id)
        return {
            "name": _("Add Orders"),
            "view_type": "form",
            "view_mode": "form",
            "res_model": "sale.order.group.add.order",
            "view_id": False,
            "type": "ir.actions.act_window",
            "context": ctx,
            "target": "new",
        }
