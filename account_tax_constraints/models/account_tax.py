# Copyright 2009-2020 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError


class AccountTax(models.Model):
    _inherit = "account.tax"

    def unlink(self):
        for tax in self:

            products = (
                self.env["product.template"]
                .with_context(active_test=False)
                .search(
                    ["|", ("supplier_taxes_id", "=", tax.id), ("taxes_id", "=", tax.id)]
                )
            )
            if products:
                product_list = ["%s" % x.name for x in products]
                raise UserError(
                    _(
                        "You cannot delete a tax that "
                        "has been set on product records"
                        "\nAs an alterative, you can disable a "
                        "tax via the 'active' flag."
                        "\n\nProduct records: %s"
                    )
                    % product_list
                )

            aml_ids = []
            self.env.cr.execute(  # pylint: disable=E8103
                """
                SELECT id
                FROM account_move_line
                WHERE tax_line_id = %s
                """
                % tax.id
            )
            res = self.env.cr.fetchall()
            if res:
                aml_ids += [x[0] for x in res]

            aml_ids = []
            self.env.cr.execute(  # pylint: disable=E8103
                """
                SELECT account_move_line_id
                FROM account_move_line_account_tax_rel
                WHERE account_tax_id = %s
                """
                % tax.id
            )
            res = self.env.cr.fetchall()
            if res:
                aml_ids += [x[0] for x in res]
            if aml_ids:
                raise UserError(
                    _(
                        "You cannot delete a tax that "
                        "has been set on Journal Items."
                        "\n\nJournal Item IDs: %s"
                    )
                    % aml_ids
                )

        return super().unlink()
