# Copyright 2009-2020 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def post(self):
        res = super().post()
        self.mapped("line_ids")._check_analytic_dimension_policy()
        return res
