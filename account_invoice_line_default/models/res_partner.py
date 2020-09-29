# Copyright 2009-2020 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    property_in_inv_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Incoming Invoice Account",
        company_dependent=True,
        domain=[("deprecated", "=", False)],
        help="Default Account on incoming Invoices.",
    )
    property_out_inv_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Outgoing Invoice Account",
        company_dependent=True,
        domain=[("deprecated", "=", False)],
        help="Default Account on outgoing Invoices.",
    )
