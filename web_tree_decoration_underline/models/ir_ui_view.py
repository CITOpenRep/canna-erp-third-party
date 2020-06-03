# Copyright 2020 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class IrUiView(models.Model):
    """
    We remove the "decoration-uf" in the 'arch_db' field constraint
    so that we dont have to patch the rng file
    or adapt the logic of the _check_xml constraint.
    """

    _inherit = "ir.ui.view"

    @api.constrains("arch_db")
    def _check_xml(self):
        self = self.with_context(check_xml=True)
        return super()._check_xml()

    def read_combined(self, fields=None):
        res = super().read_combined(fields=fields)
        if self.env.context.get("check_xml") and "decoration-uf" in res["arch"]:
            res["arch"] = self._remove_decoration_uf(res["arch"])
        return res

    def _remove_decoration_uf(self, source):
        if "decoration-uf" in source:
            s0, s1 = source.split("decoration-uf", 1)
            s2 = s1.split('"', 2)[2]
            return s0 + self._remove_decoration_uf(s2)
        else:
            return source
