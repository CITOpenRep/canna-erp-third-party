# Copyright 2020 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    sale_order_ids = fields.Many2many(
        comodel_name="sale.order",
        compute="_compute_sale_orders",
        search="_search_sale_order_ids",
        string="Sale Orders",
    )
    sale_order_count = fields.Integer(
        compute="_compute_sale_orders", string="# of Sales Order"
    )

    def _compute_sale_orders(self):
        for po in self:
            po.sale_order_ids = po.order_line.mapped("sale_line_id.order_id")
            po.sale_order_count = len(po.sale_order_ids)

    @api.model
    def _search_sale_order_ids(self, operator, value):
        if operator == "in":
            if isinstance(value, int):
                value = [value]
            purchase_orders = self.env["purchase.order.line"].search(
                [("sale_line_id.order_id", "in", value), ("state", "!=", "cancel")]
            )
            return [("id", "in", purchase_orders.ids)]
        else:
            raise UserError(_("Unsupported operand for search!"))

    def view_sale_order(self):
        action = {}
        so_ids = [x.id for x in self.sale_order_ids]
        if so_ids:
            form = self.env.ref("sale.view_order_form")
            if len(so_ids) > 1:
                tree = self.env.ref("sale.view_order_tree")
                action.update(
                    {
                        "name": _("Sales Orders"),
                        "view_mode": "tree,form",
                        "views": [(tree.id, "tree"), (form.id, "form")],
                        "domain": [("id", "in", so_ids)],
                    }
                )
            else:
                action.update(
                    {
                        "name": _("Sales Order"),
                        "view_mode": "form",
                        "view_id": form.id,
                        "res_id": so_ids[0],
                    }
                )
            action.update(
                {
                    "context": self._context,
                    "view_type": "form",
                    "res_model": "sale.order",
                    "type": "ir.actions.act_window",
                }
            )
        return action
