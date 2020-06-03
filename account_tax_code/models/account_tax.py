# Copyright 2009-2020 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class AccountTax(models.Model):
    _inherit = "account.tax"

    code = fields.Char()

    _sql_constraints = [
        (
            "code_company_uniq",
            "unique (code,company_id)",
            "The code of the Tax must be unique per company !",
        )
    ]

    def copy(self, default=None):
        default = dict(default or {}, code=_("%s (Copy)") % (self.code or ""))
        return super().copy(default=default)

    def name_get(self):
        res = super().name_get()
        if self.env.context.get("append_code_to_tax_name"):
            for i, entry in enumerate(res):
                tax = self[i]
                if tax.code:
                    res[i] = (tax.id, "[{}] {}".format(tax.code, entry[1]))
        return res
