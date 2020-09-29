# Copyright 2019-2020 Noviat.
# Code inspired by OCA account_journal_lock_date 11.0 module
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    def _check_fiscalyear_lock_date(self):
        res = super()._check_fiscalyear_lock_date()
        self._check_journal_lock_date()
        return res

    def _check_journal_lock_date(self):
        if self.env["account.journal"]._can_bypass_journal_lock_date():
            return
        for move in self.filtered(lambda move: move.state == "posted"):
            lock_date = move.journal_id.journal_lock_date
            if lock_date and move.date <= lock_date:
                raise UserError(
                    _(
                        "You cannot post/modify entries prior to and "
                        "inclusive of the journal lock date %s"
                    )
                    % lock_date
                )
