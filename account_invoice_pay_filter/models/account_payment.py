# Copyright 2009-2020 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.onchange("amount", "currency_id")
    def _onchange_amount(self):
        res = super()._onchange_amount()
        if not res and not res.get("domain") and not res["domain"].get("journal_id"):
            _logger.error(
                "Programming Error in _on_change amount. "
                "The method does not return the journal domain."
            )
            return res
        pj_dom = res["domain"]["journal_id"]
        company = self.invoice_ids[0].company_id
        pj_dom.append(("company_id", "=", company.id))
        if self.payment_type == "inbound":
            pj_dom.append(("payment_method_in", "=", True))
        else:
            pj_dom.append(("payment_method_out", "=", True))
        pay_journals = self.env["account.journal"].search(pj_dom)
        self.journal_id = len(pay_journals) == 1 and pay_journals or False
        pj_dom = [("id", "in", pay_journals.ids)]
        return res

    @api.onchange("journal_id")
    def _onchange_journal(self):
        res = super()._onchange_journal()
        if self.journal_id and len(self.invoice_ids) == 1:
            if (
                self.payment_type == "inbound"
                and self.journal_id.payment_date_in == "invoice_date"
            ):
                self.payment_date = self.invoice_ids.invoice_date
            elif self.journal_id.payment_date_out == "invoice_date":
                self.payment_date = self.invoice_ids.invoice_date
        return res
