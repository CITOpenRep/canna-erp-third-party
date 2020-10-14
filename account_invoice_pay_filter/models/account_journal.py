# Copyright 2009-2020 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    payment_method_out = fields.Boolean(
        string="Outgoing Payment Method",
        help="If checked, this Journal becomes a Payment Method "
        "for the 'Register Payment' button on "
        "Supplier Invoices and Customer Credit Notes.",
    )
    payment_date_out = fields.Selection(
        [("invoice_date", "Invoice Date"), ("current_date", "Now")],
        string="Outgoing Payment Date",
        help="Default date for the Payment.",
        default="current_date",
    )
    payment_method_in = fields.Boolean(
        string="Incoming Payment Method",
        help="If checked, this Journal becomes a Payment Method "
        "for the 'Register Payment' button on "
        "Customer Invoices and Supplier Credit Notes.",
    )
    payment_date_in = fields.Selection(
        [("invoice_date", "Invoice Date"), ("current_date", "Now")],
        string="Incoming Payment Date",
        help="Default date for the Payment.",
        default="current_date",
    )
