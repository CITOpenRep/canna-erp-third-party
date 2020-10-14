# Copyright 2009-2020 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountFiscalPosition(models.Model):
    _inherit = "account.fiscal.position"

    company_id = fields.Many2one(
        required=True, default=lambda self: self.env.user.company_id
    )

    _sql_constraints = [
        (
            "name_company_uniq",
            "unique (name, company_id)",
            "The name of the fiscal position must be unique per company !",
        )
    ]

    @api.returns("self", lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        default.setdefault("name", _("%s (copy)") % (self.name or ""))
        return super().copy(default)

    def unlink(self):
        for fpos in self:

            partners = (
                self.env["res.partner"]
                .with_context(active_test=False)
                .search([("property_account_position_id", "=", fpos.id)])
            )
            if partners:
                partner_list = ["{} (ID:{})".format(x.name, x.id) for x in partners]
                raise UserError(
                    _(
                        "You cannot delete a fiscal position that "
                        "has been set on partner records"
                        "\nAs an alterative, you can disable a "
                        "fiscal position via the 'active' flag."
                        "\n\nPartner records: %s"
                    )
                    % partner_list
                )

            invoices = (
                self.env["account.move"]
                .with_context(active_test=False)
                .search([("fiscal_position_id", "=", fpos.id)])
            )
            if invoices:
                invoice_list = [
                    "{} (ID:{})".format(x.name == "/" and "n/a" or x.name, x.id)
                    for x in invoices
                ]
                raise UserError(
                    _(
                        "You cannot delete a fiscal position that "
                        "has been used on invoices"
                        "\nAs an alterative, you can disable a "
                        "fiscal position via the 'active' flag."
                        "\n\nInvoices: %s"
                    )
                    % invoice_list
                )

        return super().unlink()
