# Copyright 2019-2020 Noviat
# Code inspired by OCA account_journal_lock_date 11.0 module
# # License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountJournal(models.Model):

    _inherit = "account.journal"

    journal_lock_date = fields.Date(
        string="Lock date",
        help="Journal Items cannot be entered nor modified in this "
        "journal prior to the lock date.",
    )

    @api.model
    def _can_bypass_journal_lock_date(self):
        """
        This method is meant to be overridden to provide
        finer control on who can bypass the lock date.
        By default nobody can bypass the journal lock date.
        e.g.
        return self.env.user.has_group('account.group_account_manager')
        """
        return False
