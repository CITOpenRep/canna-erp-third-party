# Copyright 2009-2020 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    # 13.0 equivalent of account.invoice,name field in Odoo 12.0 and before
    invoice_description = fields.Char(
        string="Description",
        index=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        copy=False,
        help="This field will also be used as a default label on the invoice lines",
    )

    @api.model
    def fields_view_get(
        self, view_id=None, view_type=False, toolbar=False, submenu=False
    ):
        res = super().fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        context = self.env.context
        if not context.get("account_invoice_line_default"):
            if view_type == "form":
                view = etree.XML(res["arch"])
                inv_line_ids = view.xpath("//field[@name='invoice_line_ids']")
                extra_ctx = (
                    "'account_invoice_line_default': 1, "
                    "'inv_desc': invoice_description, "
                    "'inv_partner_id': partner_id"
                )
                for el in inv_line_ids:
                    ctx = el.get("context")
                    if ctx:
                        ctx_strip = ctx.rstrip("}").strip().rstrip(",")
                        ctx = ctx_strip + ", " + extra_ctx + "}"
                    else:
                        ctx = "{" + extra_ctx + "}"
                    el.set("context", str(ctx))
                res["arch"] = etree.tostring(view)
        return res


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    name = fields.Char(default=lambda self: self._default_name())
    account_id = fields.Many2one(default=lambda self: self._default_account_id())

    @api.model
    def _default_name(self):
        return self.env.context.get(
            "account_invoice_line_default"
        ) and self.env.context.get("inv_desc")

    @api.model
    def _default_account_id(self):
        ctx = self.env.context
        account = None
        if ctx.get("account_invoice_line_default"):
            if ctx.get("inv_partner_id"):
                partner = self.env["res.partner"].browse(ctx["inv_partner_id"])
                partner = partner.commercial_partner_id
                if ctx.get("default_type") in ["in_invoice", "in_refund"]:
                    account = partner.property_in_inv_account_id
                else:
                    account = partner.property_out_inv_account_id
        return account
