# Copyright 2020 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from lxml import etree

from odoo import api, models

_logger = logging.getLogger(__name__)


class IrUiView(models.Model):
    _inherit = "ir.ui.view"

    @api.model
    def get_inheriting_views_arch(self, view_id, model):
        archs = super().get_inheriting_views_arch(view_id, model)
        adp_view = self.env.ref(
            "account_analytic_dimension_policy.view_move_form", False
        )
        if adp_view and view_id == adp_view.id:
            dims = self.env["account.move.line"]._get_all_analytic_dimensions(
                self.env.company.id
            )
            archs = self._enforce_analytic_dimensions(model, archs, dims)
        return archs

    def _enforce_analytic_dimensions(self, model, archs_in, dims):
        archs = archs_in[:]
        attrs = (
            "{'required': [('%(dim)s_ui_modifier', '=', 'required')]"
            ", 'readonly': [('%(dim)s_ui_modifier', '=', 'readonly')]}"
        )
        for i, (arch, view_id) in enumerate(archs_in):
            arch_node = etree.fromstring(arch)
            upd = False
            for lines_fld in ["invoice_line_ids", "line_ids"]:
                expr_xp = "//xpath[contains(@expr, '{}')]".format(lines_fld)
                fld_nodes = arch_node.xpath(expr_xp)
                for fld_node in fld_nodes:
                    for dim in dims:
                        etree.SubElement(
                            fld_node,
                            "field",
                            name="{}_ui_modifier".format(dim),
                            invisible="1",
                        )
                        expr_dim = ".//field[@name='{}']".format(dim)
                        dim_nodes = fld_node.xpath(expr_dim)
                        for dim_node in dim_nodes:
                            upd = True
                            dim_node.set("attrs", attrs % {"dim": dim})
                            dim_node.set("force_save", "1")
            if upd:
                arch = etree.tostring(arch_node, encoding="unicode")
            archs[i] = (arch, view_id)
        return archs
