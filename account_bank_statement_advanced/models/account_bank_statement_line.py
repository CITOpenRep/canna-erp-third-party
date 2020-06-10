# Copyright 2009-2020 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, api, fields, models


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    # new fields
    statement_date = fields.Date(
        related="statement_id.date", string="Statement Date", readonly=True, store=True
    )
    val_date = fields.Date(string="Value Date")  # nl: valuta datum)
    journal_code = fields.Char(
        related="statement_id.journal_id.code",
        string="Journal Code",
        store=True,
        readonly=True,
    )
    globalisation_id = fields.Many2one(
        comodel_name="account.bank.statement.line.global",
        string="Globalisation ID",
        readonly=True,
        help="Code to identify transactions belonging to the same "
        "globalisation level within a batch payment",
    )
    globalisation_amount = fields.Monetary(
        related="globalisation_id.amount", string="Glob. Amount", readonly=True
    )
    counterparty_bic = fields.Char(
        string="Counterparty BIC", size=11, states={"confirm": [("readonly", True)]}
    )
    counterparty_number = fields.Char(
        string="Counterparty Number", states={"confirm": [("readonly", True)]}
    )
    counterparty_currency = fields.Char(
        string="Counterparty Currency", size=3, states={"confirm": [("readonly", True)]}
    )
    payment_reference = fields.Char(
        string="Payment Reference",
        size=35,
        states={"confirm": [("readonly", True)]},
        help="Payment Reference. For SEPA (SCT or SDD) transactions, "
        "the EndToEndReference is recorded in this field.",
    )
    creditor_reference_type = fields.Char(
        # To DO : change field to selection list
        string="Creditor Reference Type",
        size=35,
        states={"confirm": [("readonly", True)]},
        help="Creditor Reference Type. For SEPA (SCT) transactions, "
        "the <CdtrRefInf> type is recorded in this field."
        "\nE.g. 'BBA' for belgian structured communication "
        "(Code 'SCOR', Issuer 'BBA'",
    )
    creditor_reference = fields.Char(
        "Creditor Reference",
        size=35,  # cf. pain.001.001.003 type="Max35Text"
        states={"confirm": [("readonly", True)]},
        help="Creditor Reference. For SEPA (SCT) transactions, "
        "the <CdtrRefInf> reference is recorded in this field.",
    )
    moves_state = fields.Selection(
        string="Moves State",
        selection=[("draft", "Unposted"), ("posted", "Posted")],
        compute="_compute_moves_state",
        store=True,
    )
    # update existing fields
    state = fields.Selection(store=True)
    date = fields.Date(string="Entry Date")
    partner_id = fields.Many2one(
        domain=["|", ("parent_id", "=", False), ("is_company", "=", True)]
    )

    @api.depends("journal_entry_ids.move_id.state")
    def _compute_moves_state(self):
        for line in self:
            state = False
            moves = line.journal_entry_ids.mapped("move_id")
            states = moves.mapped("state")
            if states:
                state = any([x == "draft" for x in states]) and "draft" or "posted"
            line.moves_state = state

    @api.onchange("currency_id", "val_date", "date")
    def _onchange_currency_id(self):
        if self.currency_id and not self.amount_currency:
            self.amount_currency = self.statement_id.currency_id.with_context(
                date=self.val_date or self.date
            ).compute(self.amount, self.currency_id)
        if not self.currency_id:
            self.amount_currency = 0.0

    def unlink(self):
        glines = self.mapped("globalisation_id")
        todelete = glines.filtered(
            lambda gline: all(
                [stl_id in self.ids for stl_id in gline.bank_statement_line_ids.ids]
            )
        )
        todelete.unlink()
        return super().unlink()

    def button_cancel_reconciliation(self):
        """
        remove the account_id from the st_line for manual reconciliation
        """
        for st_line in self:
            if st_line.account_id:
                st_line.account_id = False
        super().button_cancel_reconciliation()
        return True

    def button_view_moves(self):
        self.ensure_one()
        moves = self.journal_entry_ids.mapped("move_id")
        act_move = {
            "name": _("Journal Entries"),
            "view_type": "form",
            "view_mode": "tree,form",
            "res_model": "account.move",
            "domain": [("id", "in", moves.ids)],
            "context": self._context,
            "type": "ir.actions.act_window",
        }
        return act_move

    def manual_reconcile(self):
        return {
            "type": "ir.actions.client",
            "tag": "bank_statement_reconciliation_view",
            "context": {
                "statement_line_ids": self.ids,
                "company_ids": self.mapped("company_id").ids,
            },
        }

    def automatic_reconcile(self):
        reconcile_note = ""
        statements = self.mapped("statement_id")
        for st in statements:
            st_lines = self.filtered(lambda r: r.statement_id == st)
            reconcile_note += st._automatic_reconcile(
                reconcile_note=reconcile_note, st_lines=st_lines
            )
        if reconcile_note:
            module = __name__.split("addons.")[1].split(".")[0]
            result_view = self.env.ref(
                "%s.bank_statement_automatic_reconcile_result_view_form" % module
            )
            return {
                "name": _("Automatic Reconcile remarks:"),
                "view_type": "form",
                "view_mode": "form",
                "res_model": "bank.statement.automatic.reconcile.result.view",
                "view_id": result_view.id,
                "target": "new",
                "context": dict(self.env.context, note=reconcile_note),
                "type": "ir.actions.act_window",
            }
        else:
            return True
