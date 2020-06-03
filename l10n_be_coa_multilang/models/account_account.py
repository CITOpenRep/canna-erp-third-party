# Copyright 2009-2020 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountAccount(models.Model):
    _inherit = "account.account"

    be_report_chart_ids = fields.Many2many(
        comodel_name="be.legal.financial.report.chart",
        relation="account_be_legal_report_rel",
        column1="account_id",
        column2="report_chart_id",
        string="Belgian Financial Reports",
    )
    company_country_code = fields.Char(
        compute="_compute_company_country_code",
        string="Company Country Code",
        readonly=True,
        store=True,
    )

    @api.depends("company_id.country_id")
    def _compute_company_country_code(self):
        for account in self:
            account.company_country_code = (
                account.company_id.country_id
                and account.company_id.country_id.code.upper()
            )

    @api.onchange("code")
    def _onchange_code(self):
        countries = self._get_be_scheme_countries()
        if self.code and self.company_id.country_id.code in countries:

            entry, entries = self._get_be_report_scheme_entry(self.code)

            be_chart_entries = entries.mapped("report_chart_id")
            for chart_entry in self.be_report_chart_ids:
                if (
                    chart_entry in be_chart_entries
                    and chart_entry != entry.report_chart_id
                ):
                    self.be_report_chart_ids -= chart_entry
            if entry.report_chart_id not in self.be_report_chart_ids:
                self.be_report_chart_ids += entry.report_chart_id

            if not self.env.context.get("noupdate_account_tags"):
                cf_tags = self._get_cash_flow_statement_tags()
                for tag in self.tag_ids:
                    if tag in cf_tags and tag not in entry.account_tag_ids:
                        self.tag_ids -= tag
                for new_tag in entry.account_tag_ids:
                    if new_tag not in self.tag_ids:
                        self.tag_ids += new_tag

            if not self.env.context.get("noupdate_account_type"):
                if self.user_type_id != entry.account_type_id:
                    self.user_type_id = entry.account_type_id

        if hasattr(super(AccountAccount, self), "_onchange_code"):
            super(AccountAccount, self)._onchange_code()

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """ improve performance of _update_be_reportscheme method """
        if self.env.context.get("update_be_reportscheme"):
            be_companies = (
                self.env["res.company"]
                .search([])
                .filtered(
                    lambda r: r.country_id.code in self._get_be_scheme_countries()
                )
            )
            args += [("company_id", "in", [x.id for x in be_companies])]
        return super(AccountAccount, self).search(
            args, offset=offset, limit=limit, order=order, count=count
        )

    @api.model
    def create(self, vals):
        company_id = vals.get("company_id")
        if company_id:
            company = self.env["res.company"].browse(vals["company_id"])
        else:
            company = self.env["res.company"]._company_default_get("account.account")
        if company.country_id.code in self._get_be_scheme_countries():
            entry, entries = self._get_be_report_scheme_entry(vals.get("code", ""))
            if entry:
                if entry.report_chart_id:
                    vals["be_report_chart_ids"] = [(4, entry.report_chart_id.id)]
                if not vals.get("user_type_id"):
                    vals["user_type_id"] = entry.account_type_id.id
                if not vals.get("tag_ids"):
                    vals["tag_ids"] = [(6, 0, entry.account_tag_ids.ids)]
        return super(AccountAccount, self).create(vals)

    def write(self, vals):
        if "code" in vals:
            if len(self) == 1 and vals.get("code") != self.code:
                company = (
                    vals.get("company_id")
                    and self.env["res.company"].browse(vals["company_id"])
                    or self.company_id
                )
                if company.country_id.code in self._get_be_scheme_countries():
                    update = []
                    old, entries = self._get_be_report_scheme_entry(self.code)
                    if old.report_chart_id:
                        update.append((3, old.report_chart_id.id))
                    new, entries = self._get_be_report_scheme_entry(
                        vals.get("code", "")
                    )
                    if new.report_chart_id:
                        update.append((4, new.report_chart_id.id))
                    if update:
                        vals["be_report_chart_ids"] = vals.get(
                            "be_report_chart_ids", []
                        )
                        vals["be_report_chart_ids"].extend(update)
        return super(AccountAccount, self).write(vals)

    def _get_be_scheme_countries(self):
        """
        Use this method to extend the list of countries for which you want to
        use the Belgian BNB scheme for financial reporting purposes.
        """
        return ["BE"]

    def _get_cash_flow_statement_tags(self):
        """
        Use this method if you have changed the standard
        'account_reports' Cash Flow report
        """
        tags = self.env["account.account.tag"]
        refs = [
            "account.account_tag_operating",
            "account.account_tag_financing",
            "account.account_tag_investing",
        ]
        for ref in refs:
            tags += self.env.ref(ref)
        return tags

    def _get_be_report_scheme_entry(self, code):
        entries = self.env["be.legal.financial.report.scheme"].search([])
        entry = entries.filtered(
            lambda r: r.account_group == code[0 : len(r.account_group)]
        )
        if len(entry) > 1:
            raise UserError(
                _(
                    "Configuration Error in the "
                    "Belgian Legal Financial Report Scheme."
                )
            )
        return entry, entries
