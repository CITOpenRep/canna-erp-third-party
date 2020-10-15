# Copyright 2019-2020 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrderGroupInvoiceCreate(models.TransientModel):
    _name = "sale.order.group.invoice.create"
    _description = "Create Sale Order Group Invoice"

    sale_order_group_id = fields.Many2one(
        comodel_name="sale.order.group", string="Sale Order Group", readonly=True
    )
    date_invoice = fields.Date(string="Invoice Date")

    def create_invoice(self):
        ctx = dict(self.env.context, date_invoice=self.date_invoice)
        for sog in self:
            orders = sog.with_context(ctx).sale_order_group_id.sale_order_ids
            invoices = orders._create_invoices()
        return invoices
