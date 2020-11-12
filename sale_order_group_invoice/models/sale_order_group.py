# Copyright 2019-2020 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, api, fields, models, tools


class SaleOrderGroup(models.Model):
    _inherit = "sale.order.group"

    disable_invoice_create = fields.Boolean(compute="_compute_invoice_flags")
    view_invoices_invisible = fields.Boolean(compute="_compute_invoice_flags")

    @api.depends("sale_order_ids")
    def _compute_invoice_flags(self):
        for sog in self:
            sog.view_invoices_invisible = True
            sog.disable_invoice_create = True
            invoice_states = list(set(sog.sale_order_ids.mapped("invoice_status")))
            if any(state == "to invoice" for state in invoice_states):
                sog.disable_invoice_create = False
            invoices = sog.sale_order_ids.mapped("invoice_ids")
            if invoices:
                sog.view_invoices_invisible = False
                invoice_states = invoices.mapped("state")
                if "open" in invoice_states or "paid" in invoice_states:
                    sog.disable_invoice_create = True

    def create_invoice(self):
        self.ensure_one()
        ctx = dict(self.env.context, default_sale_order_group_id=self.id)
        return {
            "name": _("Create Invoice"),
            "view_type": "form",
            "view_mode": "form",
            "res_model": "sale.order.group.invoice.create",
            "view_id": False,
            "type": "ir.actions.act_window",
            "context": ctx,
            "target": "new",
        }

    def view_invoices(self):
        self.ensure_one()
        invoices = self.sale_order_ids.mapped("invoice_ids")
        action = self.env["ir.actions.act_window"].for_xml_id(
            "account", "action_move_out_invoice_type"
        )
        domain = tools.safe_eval(action.get("domain") or "[]")
        domain += [("id", "in", invoices.ids)]
        action.update({"domain": domain})
        return action
