# Copyright 2009-2020 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountTaxReportLine(models.Model):
    _name = "account.tax.report.line"
    _inherit = ["account.tax.report.line", "l10n.be.chart.common"]

    @api.depends("name", "code")
    def name_get(self):
        result = []
        for case in self:
            if case.code:
                name = " - ".join([case.code, case.name])
            else:
                name = case.name
            result.append((case.id, name))
        return result
