# Copyright 2009-2020 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    force_encoding = fields.Boolean(
        string="Force Encoding",
        copy=False,
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Accept the encoding of this invoice although "
        "it looks like a duplicate.",
    )

    @api.constrains("state")
    def _check_duplicate_supplier_reference(self):
        """
        Replace the standard addons _check_duplicate_supplier_reference
        since this one is too restrictive (blocking) for certain use cases.
        """
        for move in self:
            if (
                move.state == "posted"
                and move.is_purchase_document()
                and not move.force_encoding
            ):
                move._check_si_duplicate()

    def _get_dup_domain(self):
        """
        Override this method to customize customer specific
        duplicate check query.
        """
        return [
            ("type", "=", self.type),
            ("commercial_partner_id", "=", self.commercial_partner_id.id),
            ("state", "=", "posted"),
            ("invoice_payment_state", "!=", "paid"),
            ("company_id", "=", self.company_id.id),
            ("id", "!=", self.id),
        ]

    def _get_dup_domain_extra(self):
        """
        Extra search term to detect duplicates in case no
        supplier invoice number has been specified.
        """
        return [
            ("invoice_date", "=", self.invoice_date),
            ("amount_total", "=", self.amount_total),
        ]

    def _get_dup(self):
        """
        Override this method to customize customer specific
        duplicate check logic
        """
        # find duplicates by date, amount
        domain = self._get_dup_domain()
        # add supplier invoice number
        if self.ref:
            dom_dups = domain + [("ref", "ilike", self.ref)]
        else:
            dom_dups = domain + self._get_dup_domain_extra()
        return self.search(dom_dups)

    def _check_si_duplicate(self):
        dups = self._get_dup()
        if dups:
            raise UserError(
                _(
                    "This Vendor Bill has already been encoded !"
                    "\nDuplicate Journal Entry: %s"
                )
                % ", ".join([x.name for x in dups])
            )
