# Copyright 2009-2020 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    def import_lines(self):
        self.ensure_one()
        view = self.env.ref("stock_level_import.stock_level_import_view_form")
        return {
            "name": _("Import File"),
            "view_type": "form",
            "view_mode": "form",
            "res_model": "stock.level.import",
            "view_id": view.id,
            "target": "new",
            "type": "ir.actions.act_window",
        }
