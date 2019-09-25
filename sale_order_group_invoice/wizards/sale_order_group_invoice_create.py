# -*- coding: utf-8 -*-
# Copyright 2019 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
from openerp.exceptions import Warning as UserError


class SaleOrderGroupInvoiceCreate(models.TransientModel):
    _name = 'sale.order.group.invoice.create'
    _description = 'Create Sale Order Group Invoice'

    sale_order_group_id = fields.Many2one(
        comodel_name='sale.order.group',
        string='Sale Order Group',
        readonly=True)
    keep_references = fields.Boolean(
        string='Keep references from original invoices', default=True)
    date_invoice = fields.Date(string='Invoice Date')

    @api.multi
    def create_invoice(self):
        self.ensure_one()
        orders = self.sale_order_group_id.sale_order_ids
        try:
            orders.signal_workflow('manual_invoice')
            invoices = orders.mapped('invoice_ids')
            invoices.do_merge(keep_references=self.keep_references,
                              date_invoice=self.date_invoice)
        except Exception:
            raise UserError(_("Invoice creation failed"))
        return True
